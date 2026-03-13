import os
import genome
import sys
import creature
import pybullet as p
import time
import random
import numpy as np

def main(csv_file):
    # Ensure the file actually exists before trying to open it
    assert os.path.exists(csv_file), f"Tried to load {csv_file} but it does not exist"

    # Connect in DIRECT mode (no GUI) for speed
    p.connect(p.DIRECT)
    p.setPhysicsEngineParameter(enableFileCaching=0)
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    
    plane_shape = p.createCollisionShape(p.GEOM_PLANE)
    floor = p.createMultiBody(plane_shape, plane_shape)
    p.setGravity(0, 0, -10)

    # Generate creature from DNA
    cr = creature.Creature(gene_count=1)
    dna = genome.Genome.from_csv(csv_file)
    cr.update_dna(dna)
    
    # Save to XML/URDF
    with open('test.urdf', 'w') as f:
        f.write(cr.to_xml())
        
    # Load into simulation
    rob1 = p.loadURDF('test.urdf')
    
    # Air drop it at a starting height
    p.resetBasePositionAndOrientation(rob1, [0, 0, 2.5], [0, 0, 0, 1])
    start_pos, _ = p.getBasePositionAndOrientation(rob1)

    # Simulation parameters
    elapsed_time = 0
    wait_time = 1.0 / 240.0  # standard PyBullet step
    total_time = 30          # seconds to run
    step = 0
    
    while True:
        p.stepSimulation()
        step += 1
        
        # Update motor neurons every 24 steps (approx 10Hz)
        if step % 24 == 0:
            motors = cr.get_motors()
            assert len(motors) == p.getNumJoints(rob1), "Joint count mismatch!"
            
            for jid in range(p.getNumJoints(rob1)):
                mode = p.VELOCITY_CONTROL
                vel = motors[jid].get_output()
                p.setJointMotorControl2(
                    bodyIndex=rob1,
                    jointIndex=jid,
                    controlMode=mode,
                    targetVelocity=vel
                )
            
            new_pos, _ = p.getBasePositionAndOrientation(rob1)
            dist_moved = np.linalg.norm(np.asarray(start_pos) - np.asarray(new_pos))
            print(f"Current distance: {dist_moved:.4f}")

        elapsed_time += wait_time
        if elapsed_time > total_time:
            break

    print("\n" + "="*30)
    print(f"TOTAL DISTANCE MOVED: {dist_moved:.4f}")
    print("="*30)

if __name__ == "__main__":
    # Check if a filename was provided in the terminal
    if len(sys.argv) != 2:
        print("Usage: python playback_test.py <csv_filename>")
        sys.exit(1)
        
    main(sys.argv[1])