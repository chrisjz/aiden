using UnityEngine;
using UnityEngine.InputSystem;
using CandyCoded.env;

public class MenuToggle : MonoBehaviour
{
    public GameObject menuCanvas;
    public GameObject firstPersonCanvas;
    public PlayerInput playerInput;
    public PlayerLook playerLook;
    public GameObject buttonUserRecordingStart;
    public GameObject buttonUserRecordingStop;

    private bool isMenuVisible = false;

    void Update()
    {
        env.TryParseEnvironmentVariable("AUDITORY_ENABLE", out bool isAuditoryEnabled);
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
                buttonUserRecordingStart.SetActive(isAuditoryEnabled);
                buttonUserRecordingStop.SetActive(isAuditoryEnabled);
            }
            else
            {
                Cursor.lockState = CursorLockMode.Locked; // Lock the cursor
                Cursor.visible = false;
            }
        }
    }
}
