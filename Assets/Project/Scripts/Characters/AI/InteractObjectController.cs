using UnityEngine;
using System.Collections.Generic;

public class InteractObjectController : MonoBehaviour
{
    public float interactionRange = 1.8f;

    [Tooltip("Output debug logs to console")]
    public bool debugMode = false;

    private Animator _anim;

    private MoveableObject _interactableObject;

    private Dictionary<string, string> _availableActions = new Dictionary<string, string>();

    private const string _animBoolName = "isOpen_Obj_";

    private HashSet<GameObject> _detectedObjects = new HashSet<GameObject>();

    private bool showInteractMsg;

    private GUIStyle guiStyle;

    private string msg;

    void Start()
    {
        // Initialize the animator for interaction
        _anim = GetComponent<Animator>();
        _anim.enabled = false;

        // Initialize identifier for a moveable object
        _interactableObject = GetComponent<MoveableObject>();

        //setup GUI style settings for user prompts
        setupGui();
    }

    void Update()
    {
        // Check if a player is within the trigger area before allowing interaction  
        if ((Input.GetKeyUp(KeyCode.E) || Input.GetButtonDown("Fire1")) && _detectedObjects.Count > 0)
        {
            PerformAction($"Toggle_{_interactableObject.objectNumber}");
        }
    }

    public Dictionary<string, string> GetAvailableActions()
    {
        return new Dictionary<string, string>(_availableActions);
    }

    public void PerformAction(string action)
    {
        if (_availableActions.ContainsKey(action))
        {
            if (action.StartsWith("Toggle_"))
            {
                int objectNumber = int.Parse(action.Split('_')[1]);
                string animBoolNameNum = _animBoolName + objectNumber.ToString();

                bool isOpen = _anim.GetBool(animBoolNameNum);
                _anim.enabled = true;
                _anim.SetBool(animBoolNameNum, !isOpen);

                UpdateAvailableActions(objectNumber, !isOpen);
            }
            else
            {
                Debug.LogWarning($"Action {action} is not yet implemented.");
            }
        }
        else
        {
            Debug.LogError($"Action {action} is not available.");
        }
    }

    public void UpdateAvailableActions(int objectNumber, bool isOpen)
    {
        string actionKey = $"Toggle_{objectNumber}";
        string actionDescription = isOpen ? "Close" : "Open";
        if (debugMode) Debug.Log($"Updating available actions of key {actionKey} with description {actionDescription}");

        if (_availableActions.ContainsKey(actionKey))
        {
            _availableActions[actionKey] = actionDescription;
            // showInteractMsg = true;
            msg = getGuiMsg(isOpen);
        }
        else
        {
            _availableActions.Add(actionKey, actionDescription);
        }
    }


    private void OnTriggerEnter(Collider other)
    {
        // Check if the object has a CharacterController
        // TODO: Only allow characters to interact if facing object
        if (other.GetComponent<CharacterController>() != null)
        {
            _detectedObjects.Add(other.gameObject);
            UpdateAvailableActionsForDetectedObjects();

            // Display the GUI message if the collider is a player
            if (other.tag == "Player")
            {
                showInteractMsg = true;
            }
        }
    }

    private void OnTriggerExit(Collider other)
    {
        // Remove the object if it exits the trigger
        if (_detectedObjects.Contains(other.gameObject))
        {
            _detectedObjects.Remove(other.gameObject);
            UpdateAvailableActionsForDetectedObjects();

            // Hide the GUI message if the collider is a player
            if (other.tag == "Player")
            {
                showInteractMsg = false;
            }
        }
    }

    public void UpdateAvailableActionsForDetectedObjects()
    {
        _availableActions.Clear();

        if (_interactableObject != null)
        {
            int objectNumber = _interactableObject.objectNumber;
            string animBoolNameNum = _animBoolName + objectNumber.ToString();

            bool isOpen = _anim.GetBool(animBoolNameNum);
            UpdateAvailableActions(objectNumber, isOpen);

            if (debugMode)
            {
                Debug.Log("Updated available actions:");
                foreach (var action in GetAvailableActions())
                {
                    Debug.Log($"Action: {action.Key}, Description: {action.Value}");
                }
            }
        }
        else
        {
            Debug.LogError("Current object is missing a moveable object component.");
        }
    }


    #region GUI Config

    //configure the style of the GUI
    private void setupGui()
    {
        guiStyle = new GUIStyle();
        guiStyle.fontSize = 16;
        guiStyle.fontStyle = FontStyle.Bold;
        guiStyle.normal.textColor = Color.white;
        msg = "Press E/Fire1 to Open";
    }

    private string getGuiMsg(bool isOpen)
    {
        string rtnVal;
        if (isOpen)
        {
            rtnVal = "Press E/Fire1 to Close";
        }
        else
        {
            rtnVal = "Press E/Fire1 to Open";
        }

        return rtnVal;
    }

    void OnGUI()
    {
        if (showInteractMsg)  //show on-screen prompts to user for guide.
        {
            Debug.Log("Show interactions");
            GUI.Label(new Rect(50, Screen.height - 50, 200, 50), msg, guiStyle);
        }
    }
    //End of GUI Config --------------
    #endregion
}
