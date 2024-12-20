using UnityEngine;
using UnityEngine.InputSystem;
using CandyCoded.env;

public class AgentMenuToggle : MonoBehaviour
{
    public GameObject menuCanvas;
    public AutoScrollManager agentAutoScrollManager;
    public GameObject firstPersonCanvas;
    public GameObject playerChatCanvas;
    public GameObject mainMenuCanvas;
    public PlayerInput playerInput;
    public PlayerLook playerLook;
    public GameObject buttonSubmitAISpeak;
    public GameObject buttonSubmitAIVisual;
    public GameObject buttonSubmitUserRecording;
    public bool enableMenu = true;

    private bool isMenuVisible = false;

    void Update()
    {
        if (!enableMenu)
        {
            return;
        }

        env.TryParseEnvironmentVariable("AUDITORY_LANGUAGE_ENABLE", out bool isAuditoryLanguageEnabled);
        env.TryParseEnvironmentVariable("VISION_ENABLE", out bool isVisionEnabled);
        env.TryParseEnvironmentVariable("VOCAL_ENABLE", out bool isVocalEnabled);
        if (Input.GetKeyDown(KeyCode.BackQuote)) // KeyCode for the tilde (~) key
        {
            isMenuVisible = !isMenuVisible;
            menuCanvas.SetActive(isMenuVisible);
            firstPersonCanvas.SetActive(!isMenuVisible);
            playerInput.enabled = !isMenuVisible;
            playerLook.enabled = !isMenuVisible;

            // Lock or unlock the cursor based on the menu state
            if (isMenuVisible)
            {
                Cursor.lockState = CursorLockMode.None; // Unlock the cursor
                Cursor.visible = true;

                // Toggle button visibilites based on respective APIs availability
                buttonSubmitAIVisual.SetActive(isVisionEnabled);
                buttonSubmitAISpeak.SetActive(isVocalEnabled);
                buttonSubmitUserRecording.SetActive(isAuditoryLanguageEnabled);

                // Disable agent output auto scrolling
                agentAutoScrollManager.autoScrollEnabled = false;

                mainMenuCanvas.SetActive(false);
                playerChatCanvas.SetActive(false);
            }
            else
            {
                Cursor.lockState = CursorLockMode.Locked; // Lock the cursor
                Cursor.visible = false;
                agentAutoScrollManager.autoScrollEnabled = true;
            }
        }
    }
}
