using UnityEngine;
using UnityEngine.InputSystem;

public class MainMenu : MonoBehaviour
{
    public GameObject menuCanvas;
    public GameObject agentMenuCanvas;
    public GameObject firstPersonCanvas;
    public GameObject screenMain;
    public GameObject screenControls;
    public GameObject screenExit;
    public PlayerInput playerInput;
    public PlayerLook playerLook;

    private bool isMenuVisible = false;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            ToggleMenu();
        }
    }

    private void ToggleMenu()
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

            agentMenuCanvas.SetActive(false);
            screenMain.SetActive(true);
            screenControls.SetActive(false);
            screenExit.SetActive(false);
        }
        else
        {
            Cursor.lockState = CursorLockMode.Locked; // Lock the cursor
            Cursor.visible = false;
        }
    }

    public void Back()
    {
        ToggleMenu();
    }

    public void Controls()
    {
        screenControls.SetActive(true);
        screenMain.SetActive(false);
        screenExit.SetActive(false);
    }

    public void ExitPrompt()
    {
        screenExit.SetActive(true);
        screenMain.SetActive(false);
        screenControls.SetActive(false);
    }

    public void ExitConfirm()
    {
        Application.Quit();
    }

    public void Resume()
    {
        ToggleMenu();
    }
}
