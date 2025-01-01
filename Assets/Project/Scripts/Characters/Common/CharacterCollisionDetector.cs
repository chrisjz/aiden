using UnityEngine;

public class CharacterCollisionDetector : MonoBehaviour
{
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

        // Determine the collision region (front, back, sides, top)
        string region = GetCollisionRegion(localCollisionPoint);

        if (region != "Unknown")
        {
            Debug.Log($"Collision detected at: {region} with object: {hit.collider.gameObject.name}");
        }
    }

    private string GetCollisionRegion(Vector3 localCollisionPoint)
    {
        // Normalize to mitigate uneven scaling or offsets
        localCollisionPoint.Normalize();

        Debug.Log($"Collision detected point: {localCollisionPoint}");

        // TODO: Add collisions for top and bottom, such as for hitting roof or falling
        // TODO: Add finer collision output e.g. front-left
        // TODO: Support collision detection on body parts
        if (localCollisionPoint.z > 0.5f) return "Front";
        if (localCollisionPoint.z < -0.5f) return "Back";
        if (localCollisionPoint.x > 0.5f) return "Right";
        if (localCollisionPoint.x < -0.5f) return "Left";

        return "Unknown";
    }
}
