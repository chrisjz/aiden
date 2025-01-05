using UnityEngine;

public class CharacterCollisionDetector : MonoBehaviour
{
    [System.Serializable]
    public struct CollisionInfo
    {
        public GameObject collidedObject;
        public string region;

        public CollisionInfo(GameObject obj, string reg)
        {
            collidedObject = obj;
            region = reg;
        }
    }

    [Tooltip("The most recent collision detected.")]
    public CollisionInfo lastDetectedCollision;

    [Tooltip("Output debug logs to console")]
    public bool debugMode = false;

    private CharacterController characterController;

    private void Start()
    {
        characterController = GetComponent<CharacterController>();
        if (characterController == null)
        {
            Debug.LogError("CharacterCollisionDetector requires a CharacterController component.");
        }

        // Initialize with default empty collision
        ClearDetectedCollisions();
    }

    public void ClearDetectedCollisions()
    {
        lastDetectedCollision = new CollisionInfo(null, "None");
    }

    private void OnControllerColliderHit(ControllerColliderHit hit)
    {
        // Ignore collisions with the "IgnoreTactile" layer
        if (hit.collider.gameObject.layer == LayerMask.NameToLayer("IgnoreTactile"))
        {
            return;
        }

        // Get the collision point
        Vector3 collisionPoint = hit.point;

        // Calculate the local position relative to the AI agent
        Vector3 localCollisionPoint = transform.InverseTransformPoint(collisionPoint);

        // Determine the collision region (front, back, sides)
        string region = GetCollisionRegion(localCollisionPoint);

        // Update the last detected collision
        // TODO: Change to check if there's a current collision instead and store all of these as a list.
        lastDetectedCollision = new CollisionInfo(hit.collider.gameObject, region);
        if (debugMode) Debug.Log($"Collision detected at: {region} with object: {hit.collider.gameObject.name}");
    }

    private string GetCollisionRegion(Vector3 localCollisionPoint)
    {
        // TODO: Add collisions for top and bottom, such as for hitting roof or falling
        // TODO: Add finer collision output e.g. front-left
        // TODO: Support collision detection on body parts

        // Normalize to mitigate uneven scaling or offsets
        localCollisionPoint.Normalize();

        // Log collision point for debugging if enabled
        if (debugMode) Debug.Log($"Collision detected location: {localCollisionPoint}");

        // Check for undefined regions (e.g., ceiling collision)
        if (Mathf.Approximately(localCollisionPoint.x, 0) && Mathf.Approximately(localCollisionPoint.z, 0))
        {
            return "Unknown";
        }

        // Determine region based on absolute values of x and z
        if (Mathf.Abs(localCollisionPoint.x) > Mathf.Abs(localCollisionPoint.z))
        {
            // Dominant axis is x
            return localCollisionPoint.x > 0 ? "Right" : "Left";
        }
        else
        {
            // Dominant axis is z
            return localCollisionPoint.z > 0 ? "Front" : "Back";
        }
    }

    private void OnDrawGizmosSelected()
    {
        // Draw the character controller's collision radius for debugging
        if (characterController != null)
        {
            Gizmos.color = Color.blue;
            Gizmos.DrawWireSphere(transform.position, characterController.radius + 0.1f);
        }
    }
}
