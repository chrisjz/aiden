using UnityEngine;
using UnityEngine.InputSystem;

public class MainMenu : MonoBehaviour
{
    public GameObject menuCanvas;
    public GameObject agentMenuCanvas;
    public GameObject firstPersonCanvas;
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
        }
        else
        {
            Cursor.lockState = CursorLockMode.Locked; // Lock the cursor
            Cursor.visible = false;
        }
    }

    public void Exit()
    {
        Application.Quit();
    }

    public void Resume()
    {
        ToggleMenu();
    }
}
