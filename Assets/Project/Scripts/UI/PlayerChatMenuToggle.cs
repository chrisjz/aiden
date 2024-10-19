using UnityEngine;
using UnityEngine.InputSystem;
using CandyCoded.env;
using TMPro;
using UnityEngine.UI;

public class PlayerChatMenuToggle : MonoBehaviour
{
    public GameObject menuCanvas;
    public string AIAgentTagName = "AI";
    public string playerTagName = "Player";
    public AutoScrollManager agentAutoScrollManager;
    public GameObject agentDebugMenuCanvas;
    public GameObject firstPersonCanvas;
    public GameObject mainMenuCanvas;
    public PlayerInput playerInput;
    public PlayerLook playerLook;
    public GameObject buttonSubmitUserRecording;
    public Button hideButton;

    // Public variable to set the distance range, default to 3 units
    public float distanceToAI = 3.0f;
    public TMP_Text logOutput;

    private bool isMenuVisible = false;
    private GameObject aiAgent;
    private GameObject player;

    void Start()
    {
        hideButton.onClick.AddListener(HideMenu);
        // Find the AI GameObject by tag
        aiAgent = GameObject.FindGameObjectWithTag(AIAgentTagName);
        player = GameObject.FindGameObjectWithTag(playerTagName);
    }

    void Update()
    {
        if (aiAgent == null) return; // If AI is not found, do nothing

        // Calculate the distance between the player and the AI
        float distance = Vector3.Distance(player.transform.position, aiAgent.transform.position);

        // Check if the player presses the 'T' key and is within the allowed distance to show the menu
        if (Input.GetKeyDown(KeyCode.T) && !isMenuVisible)
        {
            if (distance <= distanceToAI)
            {
                ToggleMenuVisibility(true);
            }
            else
            {
                if (logOutput != null) logOutput.text += $"<color=#C0C0C0>Cannot initiate a chat, not close enough to an AI agent.</color>\n";
            }
        }

        // Automatically hide the menu if the player moves out of range
        if (isMenuVisible && distance > distanceToAI)
        {
            ToggleMenuVisibility(false);
        }
    }

    private void ToggleMenuVisibility(bool? visible = null)
    {
        // If `visible` is passed, set to that value, otherwise toggle the current visibility
        isMenuVisible = visible ?? !isMenuVisible;

        menuCanvas.SetActive(isMenuVisible);
        firstPersonCanvas.SetActive(!isMenuVisible);
        playerInput.enabled = !isMenuVisible;
        playerLook.enabled = !isMenuVisible;

        // Lock or unlock the cursor based on the menu state
        if (isMenuVisible)
        {
            Cursor.lockState = CursorLockMode.None; // Unlock the cursor
            Cursor.visible = true;

            // Set button visibility based on whether auditory language is enabled
            env.TryParseEnvironmentVariable("AUDITORY_LANGUAGE_ENABLE", out bool isAuditoryLanguageEnabled);
            buttonSubmitUserRecording.SetActive(isAuditoryLanguageEnabled);

            // Disable agent output auto-scrolling
            agentAutoScrollManager.autoScrollEnabled = false;

            // Hide main menu canvas if it's visible
            mainMenuCanvas.SetActive(false);
        }
        else
        {
            Cursor.lockState = CursorLockMode.Locked; // Lock the cursor
            Cursor.visible = false;
            agentAutoScrollManager.autoScrollEnabled = true;
        }
    }

    private void HideMenu()
    {
        ToggleMenuVisibility(false);
    }

    public GameObject GetCurrentAIAgent()
    {
        return aiAgent;
    }
}
