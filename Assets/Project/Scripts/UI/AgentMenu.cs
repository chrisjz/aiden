using UnityEngine;
using UnityEngine.InputSystem;
using CandyCoded.env;

public class AgentMenu : MonoBehaviour
{
    public GameObject menuCanvas;
    public GameObject firstPersonCanvas;
    public GameObject playerChatCanvas;
    public PlayerInput playerInput;
    public PlayerLook playerLook;
    public GameObject sectionLog;
    public GameObject sectionControl;
    public GameObject sectionMemory;
    public GameObject sectionConfiguration;
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

                playerChatCanvas.SetActive(false);
            }
            else
            {
                Cursor.lockState = CursorLockMode.Locked; // Lock the cursor
                Cursor.visible = false;
            }
        }
    }

    public void OpenSectionLog()
    {
        sectionLog.SetActive(true);
        sectionControl.SetActive(false);
        sectionMemory.SetActive(false);
        sectionConfiguration.SetActive(false);
    }

    public void OpenSectionControl()
    {
        sectionLog.SetActive(false);
        sectionControl.SetActive(true);
        sectionMemory.SetActive(false);
        sectionConfiguration.SetActive(false);
    }

    public void OpenSectionMemory()
    {
        sectionLog.SetActive(false);
        sectionControl.SetActive(false);
        sectionMemory.SetActive(true);
        sectionConfiguration.SetActive(false);
    }

    public void OpenSectionConfiguration()
    {
        sectionLog.SetActive(false);
        sectionControl.SetActive(false);
        sectionMemory.SetActive(false);
        sectionConfiguration.SetActive(true);
    }
}
