using StarterAssets;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class PerspectiveSwitcher : MonoBehaviour
{
    public Toggle perspectiveToggle;  // The toggle/checkbox UI element
    public Camera playerCamera;    // Assign the player's camera
    public Camera aiCamera;        // Assign the AI's camera
    public AudioListener playerAudioListener;  // Assign the player's audio listener
    public AudioListener aiAudioListener;  // Assign the AI's audio listener
    public GameObject playerController;  // The player's controller or movement script
    public RenderTexture aiRenderTexture; // The RenderTexture assigned to the AI camera
    public TMP_Text logOutput;

    private CharacterController characterController;
    private PlayerLook playerLook;
    private ThirdPersonController thirdPersonController;
    private bool isPlayerPerspective = true; // Start in the player's perspective

    void Start()
    {
        characterController = playerController.GetComponent<CharacterController>();
        thirdPersonController = playerController.GetComponent<ThirdPersonController>();
        playerLook = playerCamera.GetComponent<PlayerLook>();

        // Ensure that we start with the correct camera and controls enabled
        SwitchToPlayerPerspective();
    }

    void Update()
    {
        // Check for Tab key press to toggle perspectives
        if (Input.GetKeyDown(KeyCode.Tab))
        {
            TogglePlayerPerspective();
            perspectiveToggle.isOn = !isPlayerPerspective;
        }
    }

    void TogglePlayerPerspective()
    {
        if (isPlayerPerspective)
        {
            SwitchToAIPerspective();
        }
        else
        {
            SwitchToPlayerPerspective();
        }
    }

    public bool GetIsPlayerPerspective()
    {
        return isPlayerPerspective;
    }

    public void SetIsPlayerPerspective(bool toggle)
    {
        isPlayerPerspective = toggle;
        TogglePlayerPerspective();
    }

    void SwitchToPlayerPerspective()
    {
        // Enable player's camera, audio listener, and controls
        playerCamera.enabled = true;
        playerAudioListener.enabled = true;

        // Enable player movement components
        if (characterController != null) characterController.enabled = true;
        if (playerLook != null) playerLook.enabled = true;
        if (thirdPersonController != null) thirdPersonController.enabled = true;

        // Disable AI's camera and audio listener
        aiCamera.enabled = false;
        aiAudioListener.enabled = false;

        // Swap the MainCamera tag
        aiCamera.tag = "Untagged"; // Remove MainCamera tag from AI's camera
        playerCamera.tag = "MainCamera"; // Assign MainCamera tag to player's camera

        // Remove target texture from AI camera to prevent rendering to texture
        aiCamera.targetTexture = aiRenderTexture;

        isPlayerPerspective = true;
        Debug.Log("Switched to Player Perspective");

        if (logOutput != null) logOutput.text += $"<color=#C0C0C0>Switched to Player Perspective</color>\n";
    }

    void SwitchToAIPerspective()
    {
        // Enable AI's camera and audio listener
        aiCamera.enabled = true;
        aiAudioListener.enabled = true;

        // Disable player's camera, audio listener, and controls
        playerCamera.enabled = false;
        playerAudioListener.enabled = false;

        // Disable player movement components
        if (characterController != null) characterController.enabled = false;
        if (playerLook != null) playerLook.enabled = false;
        if (thirdPersonController != null) thirdPersonController.enabled = false;

        // Swap the MainCamera tag
        playerCamera.tag = "Untagged"; // Remove MainCamera tag from player's camera
        aiCamera.tag = "MainCamera"; // Assign MainCamera tag to AI's camera

        // Disable target texture to render to the screen
        aiCamera.targetTexture = null;

        isPlayerPerspective = false;
        string logOutputText = "Switched to AI Perspective";
        Debug.Log(logOutputText);

        if (logOutput != null)
        {
            logOutput.text += $"<color=#C0C0C0>{logOutputText}</color>\n";
        }
    }
}
