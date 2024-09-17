using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace AIden
{
    public class AIActionManager : MonoBehaviour
    {
        // List of predefined actions
        public enum ActionType
        {
            MoveForward,
            MoveBackward,
            TurnLeft,
            TurnRight
        }

        public Dictionary<ActionType, AIAction> ActionMap = new Dictionary<ActionType, AIAction>();

        public PlayerInputs aiInputs;
        public ThirdPersonController aiThirdPersonController;

        private void Start()
        {
            // Initialize action mappings with name and description
            ActionMap[ActionType.MoveForward] = new AIAction("Move Forward", "Move forward");
            ActionMap[ActionType.MoveBackward] = new AIAction("Move Backward", "Move backward");
            ActionMap[ActionType.TurnLeft] = new AIAction("Turn Left", "Turn left");
            ActionMap[ActionType.TurnRight] = new AIAction("Turn Right", "Turn right");
        }

        // Call an action based on the input
        public void ExecuteAction(ActionType action)
        {
            if (ActionMap.ContainsKey(action))
            {
                // Map the AIAction to the actual movement logic
                switch (action)
                {
                    case ActionType.MoveForward:
                        MoveForward();
                        break;
                    case ActionType.MoveBackward:
                        MoveBackward();
                        break;
                    case ActionType.TurnLeft:
                        TurnLeft();
                        break;
                    case ActionType.TurnRight:
                        TurnRight();
                        break;
                }
            }
            else
            {
                Debug.LogError($"Action {action} is not defined in the ActionMap.");
            }
        }

        // Move forward (move along the z-axis)
        private void MoveForward()
        {
            StartCoroutine(MoveForwardCoroutine(1.0f));  // Move forward by 1 unit
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
            StartCoroutine(MoveBackwardCoroutine(1.0f));  // Move backward by 1 unit
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
