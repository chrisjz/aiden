using System;
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
            Vector2 moveDirection = new Vector2(0, 1);  // Move forward (1 unit in the z-axis)
            aiInputs.MoveInput(moveDirection);
        }

        // Move backward (move along the negative z-axis)
        private void MoveBackward()
        {
            Vector2 moveDirection = new Vector2(0, -1);  // Move backward (1 unit in the negative z-axis)
            aiInputs.MoveInput(moveDirection);
        }

        // Turn left (rotate -90 degrees)
        private void TurnLeft()
        {
            // Rotate the character left
            aiInputs.LookInput(new Vector2(-90, 0));
        }

        // Turn right (rotate +90 degrees)
        private void TurnRight()
        {
            // Rotate the character right
            aiInputs.LookInput(new Vector2(90, 0));
        }
    }
}
