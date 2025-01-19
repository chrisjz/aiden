using UnityEngine;
using System.Collections.Generic;

namespace AIden
{
    public class InteractObjectController : MonoBehaviour
    {

        [Tooltip("Name of the interactable object (e.g., Pantry)")]
        public string objectName;

        [Tooltip("Interaction range between object and players/agents")]
        public float interactionRange = 1.8f;

        [Tooltip("Output debug logs to console")]
        public bool debugMode = false;

        [Tooltip("Mapping of animations to their labels and states")]
        // TODO: These maps should be tied to MoveableObject objects e.g. for large objects
        // with multiple sections, such as a long kitchen bench with many drawers
        public List<AnimationStateMapping> animationStateMappings;

        private Animator _anim;

        private HashSet<GameObject> _detectedObjects = new HashSet<GameObject>();

        private bool _showInteractMsg;

        private GUIStyle _guiStyle;

        private string _interactiveMsg;

        void Start()
        {
            // Initialize the animator for interaction
            _anim = GetComponent<Animator>();
            _anim.enabled = false;

            // Setup GUI style settings for user prompts
            setupGui();
        }

        void Update()
        {
            if (_detectedObjects.Count > 0)
            {
                _interactiveMsg = $"{objectName} - Actions:\n";
                for (int i = 0; i < Mathf.Min(animationStateMappings.Count, 9); i++)
                {
                    var mapping = animationStateMappings[i];
                    bool currentState = _anim.GetBool(mapping.animBoolName);
                    string stateLabel = currentState ? mapping.offLabel : mapping.onLabel;

                    _interactiveMsg += $"Press {i + 1} to {stateLabel}\n";

                    if (Input.GetKeyDown(KeyCode.Alpha1 + i))
                    {
                        PerformAction(mapping);
                    }
                }
            }
            else
            {
                _interactiveMsg = "";
            }
        }

        private void PerformAction(AnimationStateMapping mapping)
        {
            bool currentState = _anim.GetBool(mapping.animBoolName);
            _anim.enabled = true;
            _anim.SetBool(mapping.animBoolName, !currentState);

            if (debugMode) Debug.Log($"Performed action: {(currentState ? mapping.offLabel : mapping.onLabel)} on {objectName}");
        }

        private string CreateActionKey(AnimationStateMapping mapping)
        {
            string actionState = _anim.GetBool(mapping.animBoolName) ? mapping.offLabel : mapping.onLabel;
            return $"{objectName}: {actionState}";
        }

        private string GetActionDescription(AnimationStateMapping mapping)
        {
            string actionState = _anim.GetBool(mapping.animBoolName) ? mapping.offLabel : mapping.onLabel;
            return $"For the object '{objectName}' perform the action '{actionState}'";
        }

        private void OnTriggerEnter(Collider other)
        {
            if (other.GetComponent<CharacterController>() != null)
            {
                _detectedObjects.Add(other.gameObject);

                if (other.CompareTag("Player"))
                {
                    _showInteractMsg = true;
                }
                else if (other.CompareTag("AI"))
                {
                    AddActionsToAI(other);
                }
            }
        }

        private void AddActionsToAI(Collider aiCollider)
        {
            var actionManager = aiCollider.GetComponentInChildren<AIActionManager>();
            if (actionManager != null)
            {
                foreach (var mapping in animationStateMappings)
                {
                    string actionKey = CreateActionKey(mapping);
                    string actionDescription = GetActionDescription(mapping);

                    actionManager.AddObjectAction(actionKey, new AIAction(actionKey, actionDescription));
                }
            }
        }

        private void OnTriggerExit(Collider other)
        {
            if (_detectedObjects.Contains(other.gameObject))
            {
                _detectedObjects.Remove(other.gameObject);

                if (other.CompareTag("Player"))
                {
                    _showInteractMsg = false;
                }
                else if (other.CompareTag("AI"))
                {
                    RemoveActionsFromAI(other);
                }
            }
        }

        private void RemoveActionsFromAI(Collider aiCollider)
        {
            var actionManager = aiCollider.GetComponentInChildren<AIActionManager>();
            if (actionManager != null)
            {
                foreach (var mapping in animationStateMappings)
                {
                    string actionKey = CreateActionKey(mapping);
                    actionManager.RemoveObjectAction(actionKey);
                }
            }
        }

        #region GUI Config

        private void setupGui()
        {
            _guiStyle = new GUIStyle();
            _guiStyle.fontSize = 16;
            _guiStyle.fontStyle = FontStyle.Bold;
            _guiStyle.normal.textColor = Color.white;
            _interactiveMsg = "";
        }

        void OnGUI()
        {
            if (_showInteractMsg)
            {
                GUI.Label(new Rect(50, 100, 400, 100), _interactiveMsg, _guiStyle);
            }
        }

        #endregion

        [System.Serializable]
        public class AnimationStateMapping
        {
            public string animBoolName;
            public string onLabel;
            public string offLabel;
        }
    }
}
