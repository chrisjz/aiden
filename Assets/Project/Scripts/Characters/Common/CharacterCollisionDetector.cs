using System.Collections.Generic;
using UnityEngine;

public class CharacterCollisionDetector : MonoBehaviour
{
    private readonly Dictionary<GameObject, string> currentCollisions = new(); // Tracks active collisions

    [Tooltip("Radius for detecting nearby collisions.")]
    public float collisionDetectionRadius = 0.5f;

    [Tooltip("Frequency of collision updates in seconds.")]
    public float updateFrequency = 1.0f;

    private float nextUpdateTime = 0f;

    private void FixedUpdate()
    {
        // Periodically update collision state
        if (Time.time >= nextUpdateTime)
        {
            nextUpdateTime = Time.time + updateFrequency;
            UpdateCollisionState();
        }
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

        // Determine the collision region (front, back, sides, top)
        string region = GetCollisionRegion(localCollisionPoint);

        if (region != "Unknown")
        {
            // Add or update the collision state
            if (!currentCollisions.ContainsKey(hit.collider.gameObject))
            {
                Debug.Log($"Collision detected at: {region} with object: {hit.collider.gameObject.name}");
            }
            currentCollisions[hit.collider.gameObject] = region;
        }
    }

    private void UpdateCollisionState()
    {
        // Check all objects within the collision radius
        Collider[] colliders = Physics.OverlapSphere(transform.position, collisionDetectionRadius);
        HashSet<GameObject> detectedObjects = new();

        foreach (var collider in colliders)
        {
            if (collider.gameObject.layer == LayerMask.NameToLayer("IgnoreTactile"))
            {
                continue; // Skip ignored layers
            }

            // If an object is in the collision radius, keep it in the active collision list
            detectedObjects.Add(collider.gameObject);

            if (!currentCollisions.ContainsKey(collider.gameObject))
            {
                Debug.Log($"Collision started with object: {collider.gameObject.name}");
                currentCollisions[collider.gameObject] = "Unknown"; // Default to unknown region
            }
        }

        // Find objects no longer in collision and remove them
        List<GameObject> objectsToRemove = new();
        foreach (var collision in currentCollisions)
        {
            if (!detectedObjects.Contains(collision.Key))
            {
                Debug.Log($"Collision ended with object: {collision.Key.name}");
                objectsToRemove.Add(collision.Key);
            }
        }

        // Remove stale collisions
        foreach (var obj in objectsToRemove)
        {
            currentCollisions.Remove(obj);
        }
    }

    private string GetCollisionRegion(Vector3 localCollisionPoint)
    {
        // Normalize to mitigate uneven scaling or offsets
        localCollisionPoint.Normalize();

        // Determine region
        // TODO: Add collisions for top and bottom, such as for hitting roof or falling
        // TODO: Add finer collision output e.g. front-left
        // TODO: Support collision detection on body parts
        if (localCollisionPoint.z > 0.5f) return "Front";
        if (localCollisionPoint.z < -0.5f) return "Back";
        if (localCollisionPoint.x > 0.5f) return "Right";
        if (localCollisionPoint.x < -0.5f) return "Left";

        return "Unknown";
    }

    private void OnDrawGizmosSelected()
    {
        // Draw the collision detection radius in the editor for debugging
        Gizmos.color = Color.blue;
        Gizmos.DrawWireSphere(transform.position, collisionDetectionRadius);
    }
}
