import pybullet as p
import os
import copy
import concurrent.futures
from environment import setup_environment

class Simulation:
    def __init__(self, sim_id=0, physics_client_id=None):
        # We connect in DIRECT mode for background processing
        self.physicsClientId = p.connect(p.DIRECT)
        self.sim_id = sim_id

    def run_creature(self, cr, iterations=2400):
        pid = self.physicsClientId
        setup_environment(physics_client_id=pid)
        
        # Use unique filenames for parallel processes to avoid overwriting
        xml_file = f'temp_{os.getpid()}_{self.sim_id}.urdf'
        xml_str = cr.to_xml()
        with open(xml_file, 'w') as f:
            f.write(xml_str)
        
        cid = p.loadURDF(xml_file, physicsClientId=pid)

        if cid < 0:
            print(f"[ERROR] Failed to load URDF: {xml_file}")
            try:
                os.remove(xml_file)
            except Exception:
                pass
            return None
        
        p.resetBasePositionAndOrientation(cid, [5, 0, 4], [0, 0, 0, 1], physicsClientId=pid)
        
        motors = cr.get_motors()
        start_pos = None
        end_pos = None
        final_xy = (0, 0)
        
        for step in range(iterations):
            for i, motor in enumerate(motors):
                if i < p.getNumJoints(cid, physicsClientId=pid):
                    output = motor.get_output()
                    p.setJointMotorControl2(
                        cid, i, p.VELOCITY_CONTROL, 
                        targetVelocity=output * 5, 
                        force=5, 
                        physicsClientId=pid
                    )
            
            p.stepSimulation(physicsClientId=pid)
            
            try:
                pos, _ = p.getBasePositionAndOrientation(cid, physicsClientId=pid)
                if pos is None:
                    break
            except Exception as e:
                print(f"[ERROR] Position check failed for sim {self.sim_id}: {e}")
                break
            
            if pos is not None and len(pos) == 3:
                x, y, z = pos
                final_xy = (x, y)
                if start_pos is None:
                    start_pos = pos
                
                # Penalty: If creature falls off or flies away
                if abs(x) > 10 or abs(y) > 10 or z < -1.0:
                    break
                end_pos = pos
        
        result = {
            'start_pos': start_pos,
            'end_pos': end_pos,
            'final_xy': final_xy
        }

        # Cleanup: Crucial to prevent memory leaks
        p.removeBody(cid, physicsClientId=pid)
        try:
            os.remove(xml_file)
        except Exception:
            pass
        p.disconnect(physicsClientId=pid)
        return result

class ThreadedSim():
    def __init__(self, pool_size, physics_client_id=None):
        self.pool_size = pool_size

    @staticmethod
    def static_run_creature(sim_id, cr, iterations=2400, physics_client_id=None):
        try:
            sim = Simulation(sim_id)
            result = sim.run_creature(cr, iterations)
            cr.sim_result = result
        except Exception as e:
            print(f"[ERROR] Exception in worker (sim_id={sim_id}): {e}")
            cr.sim_result = None
            cr.failed = True
        return cr

    def eval_population(self, pop, iterations=2400, timeout=60):
        # Chunking the population into batches based on pool_size
        pool_args = []
        start_ind = 0
        while start_ind < len(pop.creatures):
            this_pool_args = []
            for i in range(start_ind, start_ind + self.pool_size):
                if i == len(pop.creatures):
                    break
                sim_id = i % self.pool_size
                this_pool_args.append([sim_id, pop.creatures[i], iterations, None])
            pool_args.append(this_pool_args)
            start_ind += self.pool_size
        
        new_creatures = []
        for pool_argset in pool_args:
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.pool_size) as executor:
                futures = [executor.submit(ThreadedSim.static_run_creature, *args) for args in pool_argset]
                future_to_idx = {f: i for i, f in enumerate(futures)}
                completed_idxs = set()
                
                try:
                    for future in concurrent.futures.as_completed(futures, timeout=timeout):
                        try:
                            cr = future.result()
                            new_creatures.append(cr)
                            completed_idxs.add(future_to_idx[future])
                        except Exception as e:
                            print(f"[ERROR] Future returned exception: {e}")

                except concurrent.futures.TimeoutError:
                    print("[TIMEOUT] Batch process took too long. Penalizing.")
                    # Fallback for unfinished creatures in the batch
                    for i, future in enumerate(futures):
                        if i not in completed_idxs:
                            # Use a deepcopy to avoid mutating the original pop during failure
                            idx_in_pop = len(new_creatures)
                            penalized_cr = copy.deepcopy(pop.creatures[idx_in_pop])
                            penalized_cr.sim_result = None
                            penalized_cr.failed = True
                            new_creatures.append(penalized_cr)
        
        pop.creatures = new_creatures