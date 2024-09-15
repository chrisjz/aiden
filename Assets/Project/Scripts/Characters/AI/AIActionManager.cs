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

        public Dictionary<ActionType, Action> ActionMap = new Dictionary<ActionType, Action>();

        public PlayerInputs aiInputs;

        private void Start()
        {
            // Initialize action mappings
            ActionMap[ActionType.MoveForward] = MoveForward;
            ActionMap[ActionType.MoveBackward] = MoveBackward;
            ActionMap[ActionType.TurnLeft] = TurnLeft;
            ActionMap[ActionType.TurnRight] = TurnRight;
        }

        // Call an action based on the input
        public void ExecuteAction(ActionType action)
        {
            if (ActionMap.ContainsKey(action))
            {
                ActionMap[action].Invoke();
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
