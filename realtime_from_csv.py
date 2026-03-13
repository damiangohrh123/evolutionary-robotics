import os
import genome
import sys
import creature
import pybullet as p
import time
from environment import setup_environment

def main(csv_file):
    # Fixed the f-string formatting for the error message
    assert os.path.exists(csv_file), f"Tried to load {csv_file} but it does not exist"

    # Connect to the GUI so we can watch
    p.connect(p.GUI)
    setup_environment(physics_client_id=0)
    
    # Zoom out the camera on startup for a better view of the arena
    p.resetDebugVisualizerCamera(
        cameraDistance=25,
        cameraYaw=45,
        cameraPitch=-35,
        cameraTargetPosition=[0, 0, 2]
    )

    # Initialize creature and load DNA from the specific CSV
    cr = creature.Creature(gene_count=1)
    dna = genome.Genome.from_csv(csv_file)
    cr.update_dna(dna)
    
    # Export to URDF
    with open('test.urdf', 'w') as f:
        f.write(cr.to_xml())
        
    # Load creature into the simulation
    rob1 = p.loadURDF('test.urdf')
    
    # Air drop it at the starting position (matches your experiment setup)
    p.resetBasePositionAndOrientation(rob1, [5, 0, 4], [0, 0, 0, 1])

    # Run for 2400 steps (matches the evaluation length in your GA)
    for step in range(2400):
        p.stepSimulation()
        
        motors = cr.get_motors()
        num_joints = p.getNumJoints(rob1)
        assert len(motors) == num_joints, "Motor count does not match joint count!"
        
        # Apply motor outputs to joints
        for jid in range(num_joints):
            vel = motors[jid].get_output()
            p.setJointMotorControl2(
                bodyIndex=rob1, 
                jointIndex=jid,
                controlMode=p.VELOCITY_CONTROL, 
                targetVelocity=vel * 5,  # Scaled for visible movement
                force=5
            )
        
        # Sleep to keep the simulation running at a realistic speed (approx 60fps)
        time.sleep(1.0/60.0)

if __name__ == "__main__":
    # Check for the CSV filename argument
    if len(sys.argv) != 2:
        print("Usage: python realtime_from_csv.py <csv_filename>")
        sys.exit(1)
        
    main(sys.argv[1])