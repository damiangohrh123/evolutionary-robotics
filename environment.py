import pybullet as p
import pybullet_data
import os

def make_arena(arena_size=20, wall_height=1, physics_client_id=0):
    """Create the arena with walls and floor for the mountain climbing environment."""
    wall_thickness = 0.5
    
    # --- Floor ---
    floor_collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[arena_size/2, arena_size/2, wall_thickness],
        physicsClientId=physics_client_id
    )
    floor_visual_shape = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[arena_size/2, arena_size/2, wall_thickness],
        rgbaColor=[1, 1, 0, 1],
        physicsClientId=physics_client_id
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=floor_collision_shape,
        baseVisualShapeIndex=floor_visual_shape,
        basePosition=[0, 0, -wall_thickness],
        physicsClientId=physics_client_id
    )

    # --- Horizontal Walls ---
    wall_collision_shape_h = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[arena_size/2, wall_thickness/2, wall_height/2],
        physicsClientId=physics_client_id
    )
    wall_visual_shape_h = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[arena_size/2, wall_thickness/2, wall_height/2],
        rgbaColor=[0.7, 0.7, 0.7, 1],
        physicsClientId=physics_client_id
    )

    # Create top and bottom walls
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=wall_collision_shape_h,
        baseVisualShapeIndex=wall_visual_shape_h,
        basePosition=[0, arena_size/2, wall_height/2],
        physicsClientId=physics_client_id
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=wall_collision_shape_h,
        baseVisualShapeIndex=wall_visual_shape_h,
        basePosition=[0, -arena_size/2, wall_height/2],
        physicsClientId=physics_client_id
    )

    # --- Vertical Walls ---
    wall_collision_shape_v = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[wall_thickness/2, arena_size/2, wall_height/2],
        physicsClientId=physics_client_id
    )
    wall_visual_shape_v = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[wall_thickness/2, arena_size/2, wall_height/2],
        rgbaColor=[0.7, 0.7, 0.7, 1],
        physicsClientId=physics_client_id
    )

    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=wall_collision_shape_v,
        baseVisualShapeIndex=wall_visual_shape_v,
        basePosition=[arena_size/2, 0, wall_height/2],
        physicsClientId=physics_client_id
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=wall_collision_shape_v,
        baseVisualShapeIndex=wall_visual_shape_v,
        basePosition=[-arena_size/2, 0, wall_height/2],
        physicsClientId=physics_client_id
    )

    # --- Left Bumper ---
    left_bumper_collision = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[4.0, 0.1, 2.5],
        physicsClientId=physics_client_id
    )
    left_bumper_visual = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[4.0, 0.1, 2.5],
        rgbaColor=[0, 0, 1, 0.7],
        physicsClientId=physics_client_id
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=left_bumper_collision,
        baseVisualShapeIndex=left_bumper_visual,
        basePosition=[3.0, 2, 2.5],
        physicsClientId=physics_client_id
    )

    # --- Right Bumper ---
    right_bumper_collision = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[4.0, 0.1, 2.5],
        physicsClientId=physics_client_id
    )
    right_bumper_visual = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[4.0, 0.1, 2.5],
        rgbaColor=[0, 0, 1, 0.7],
        physicsClientId=physics_client_id
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=right_bumper_collision,
        baseVisualShapeIndex=right_bumper_visual,
        basePosition=[3.0, -2, 2.5],
        physicsClientId=physics_client_id
    )

    # --- End Bumper ---
    end_bumper_collision = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[0.1, 2, 2.5],
        physicsClientId=physics_client_id
    )
    end_bumper_visual = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[0.1, 2, 2.5],
        rgbaColor=[0, 0, 1, 0.7],
        physicsClientId=physics_client_id
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=end_bumper_collision,
        baseVisualShapeIndex=end_bumper_visual,
        basePosition=[7.0, 0.0, 2.5],
        physicsClientId=physics_client_id
    )

def setup_environment(physics_client_id=0):
    """Set up the mountain climbing environment."""
    p.resetSimulation(physicsClientId=physics_client_id)
    p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=physics_client_id)
    
    # Path handling
    try:
        shapes_path = os.path.join(os.path.dirname(__file__), "shapes")
        p.setAdditionalSearchPath(shapes_path, physicsClientId=physics_client_id)
    except NameError:
        # Handles cases where __file__ isn't defined (like in some interactive shells)
        p.setAdditionalSearchPath("shapes/", physicsClientId=physics_client_id)
        
    p.setGravity(0, 0, -10, physicsClientId=physics_client_id)
    
    make_arena(20, physics_client_id=physics_client_id)
    
    mountain_position = (0, 0, -1)
    mountain_orientation = p.getQuaternionFromEuler((0, 0, 0))
    
    p.loadURDF(
        "gaussian_pyramid.urdf", 
        mountain_position, 
        mountain_orientation, 
        useFixedBase=1, 
        physicsClientId=physics_client_id
    )
    
    return 20