using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace AIden
{
    public class AIActionManager : MonoBehaviour
    {
        // List of predefined actions
        public enum BaseActionType
        {
            MoveForward,
            MoveBackward,
            TurnLeft,
            TurnRight
        }

        public Dictionary<string, AIAction> ActionMap = new Dictionary<string, AIAction>(StringComparer.OrdinalIgnoreCase);

        public PlayerInputs aiInputs;
        public ThirdPersonController aiThirdPersonController;

        private float _moveDistance = 1.0f;

        private void Start()
        {
            // Initialize action mappings with name and description
            AddOrUpdateAction(BaseActionType.MoveForward.ToString().ToLower(), new AIAction("Move Forward", "Move forward"));
            AddOrUpdateAction(BaseActionType.MoveBackward.ToString().ToLower(), new AIAction("Move Backward", "Move backward"));
            AddOrUpdateAction(BaseActionType.TurnLeft.ToString().ToLower(), new AIAction("Turn Left", "Turn left"));
            AddOrUpdateAction(BaseActionType.TurnRight.ToString().ToLower(), new AIAction("Turn Right", "Turn right"));
        }

        public void SetMoveDistance(float moveDistance)
        {
            _moveDistance = moveDistance;
        }

        // Call an action based on the input
        public void ExecuteAction(string actionKey)
        {
            if (ActionMap.TryGetValue(actionKey.ToLower(), out var action))
            {
                // Map the AIAction to the actual movement logic
                switch (actionKey.ToLower())
                {
                    case "moveforward":
                        MoveForward();
                        break;
                    case "movebackward":
                        MoveBackward();
                        break;
                    case "turnleft":
                        TurnLeft();
                        break;
                    case "turnright":
                        TurnRight();
                        break;
                    default:
                        string errorMsg = $"Action {actionKey} is not mapped to a specific function.";
                        Debug.LogError(errorMsg);
                        throw new InvalidDataException(errorMsg);
                }
            }
            else
            {
                string errorMsg = $"Action {actionKey} is not defined in the ActionMap.";
                Debug.LogError(errorMsg);
                throw new KeyNotFoundException(errorMsg);
            }
        }

        // Add or update actions (for both predefined and object-specific actions)
        public void AddOrUpdateAction(string actionKey, AIAction action)
        {
            actionKey = actionKey.ToLower();
            if (!ActionMap.ContainsKey(actionKey))
            {
                ActionMap[actionKey] = action;
                Debug.Log($"Added action: {actionKey} - {action.description}");
            }
            else
            {
                ActionMap[actionKey] = action;
                Debug.Log($"Updated action: {actionKey} - {action.description}");
            }
        }

        public void RemoveAction(string actionKey)
        {
            actionKey = actionKey.ToLower();
            if (ActionMap.ContainsKey(actionKey))
            {
                ActionMap.Remove(actionKey);
                Debug.Log($"Removed action: {actionKey}");
            }
        }

        // Move forward (move along the z-axis)
        private void MoveForward()
        {
            StartCoroutine(MoveForwardCoroutine(_moveDistance));
        }

        private IEnumerator MoveForwardCoroutine(float distance)
        {
            float movedDistance = 0.0f;
            Vector2 moveDirection = new Vector2(0, 1);  // Direction to move forward

            while (movedDistance < distance)
            {
                float step = Time.deltaTime * aiThirdPersonController.MoveSpeed;  // Distance to move this frame
                movedDistance += step;

                aiInputs.MoveInput(moveDirection);

                // Stop the movement if we have moved the desired distance
                if (movedDistance >= distance)
                {
                    aiInputs.MoveInput(Vector2.zero);  // Stop movement
                    break;
                }

                yield return null;  // Wait until the next frame
            }
        }

        // Move backward (move along the negative z-axis)
        private void MoveBackward()
        {
            StartCoroutine(MoveBackwardCoroutine(_moveDistance));
        }

        private IEnumerator MoveBackwardCoroutine(float distance)
        {
            float movedDistance = 0.0f;
            Vector2 moveDirection = new Vector2(0, -1);  // Direction to move backward

            while (movedDistance < distance)
            {
                float step = Time.deltaTime * aiThirdPersonController.MoveSpeed;  // Distance to move this frame
                movedDistance += step;

                aiInputs.MoveInput(moveDirection);

                // Stop the movement if we have moved the desired distance
                if (movedDistance >= distance)
                {
                    aiInputs.MoveInput(Vector2.zero);  // Stop movement
                    break;
                }

                yield return null;  // Wait until the next frame
            }
        }

        // Turn left (rotate -90 degrees)
        private void TurnLeft()
        {
            StartCoroutine(TurnLeftCoroutine(90f));  // Rotate by 90 degrees
        }

        // Coroutine for smooth left turn
        private IEnumerator TurnLeftCoroutine(float targetRotation)
        {
            float rotatedAngle = 0.0f;
            Vector2 lookDirection = new Vector2(-90, 0);  // Negative for left turn

            while (rotatedAngle < targetRotation)
            {
                // Rotation step size
                float rotationStep = Time.deltaTime * 90f;
                rotatedAngle += rotationStep;

                // Update look input for camera rotation
                aiInputs.LookInput(lookDirection);

                // Apply rotation to AI's body
                aiThirdPersonController.transform.rotation = Quaternion.Euler(0.0f, aiThirdPersonController.CinemachineCameraTarget.transform.rotation.eulerAngles.y, 0.0f);

                // Break out when rotation completes
                if (rotatedAngle >= targetRotation)
                {
                    aiInputs.LookInput(Vector2.zero);  // Stop rotation
                    break;
                }

                yield return null;  // Wait for the next frame
            }
        }

        // Turn right (rotate +90 degrees)
        private void TurnRight()
        {
            StartCoroutine(TurnRightCoroutine(90f));  // Rotate by 90 degrees
        }

        // Coroutine for smooth right turn
        private IEnumerator TurnRightCoroutine(float targetRotation)
        {
            float rotatedAngle = 0.0f;
            Vector2 lookDirection = new Vector2(90, 0);  // Increase look input

            while (rotatedAngle < targetRotation)
            {
                // Rotation step size
                float rotationStep = Time.deltaTime * 90f;  // Increase rotation speed here if needed
                rotatedAngle += rotationStep;

                // Update look input for camera rotation
                aiInputs.LookInput(lookDirection);

                // Apply rotation to AI's body
                aiThirdPersonController.transform.rotation = Quaternion.Euler(0.0f, aiThirdPersonController.CinemachineCameraTarget.transform.rotation.eulerAngles.y, 0.0f);

                // Break out when rotation completes
                if (rotatedAngle >= targetRotation)
                {
                    aiInputs.LookInput(Vector2.zero);  // Stop rotation
                    break;
                }

                yield return null;  // Wait for the next frame
            }
        }
    }
}
