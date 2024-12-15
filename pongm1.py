import java.awt.*;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.List;
import javax.sound.sampled.*;
import javax.swing.*;

public class PongGame extends JPanel implements KeyListener, Runnable {

    // Inner class for SoundGenerator
    public static class SoundGenerator {
        public static class Sound {
            public byte[] audioData;
            public AudioFormat format;

            public Sound(byte[] audioData, AudioFormat format) {
                this.audioData = audioData;
                this.format = format;
            }
        }

        public Sound generateBeepSound(String name, double frequency, double duration) {
            int sampleRate = 44100;
            int numSamples = (int) (duration * sampleRate);
            byte[] audioData = new byte[2 * numSamples];
            AudioFormat format = new AudioFormat(sampleRate, 16, 1, true, false);

            for (int i = 0; i < numSamples; i++) {
                double angle = 2.0 * Math.PI * i / (sampleRate / frequency);
                short sample = (short) (Math.sin(angle) * 32767);
                audioData[2 * i] = (byte) (sample & 0xff);
                audioData[2 * i + 1] = (byte) ((sample >> 8) & 0xff);
            }
            return new Sound(audioData, format);
        }

        public void playSound(Sound sound) {
            try {
                Clip clip = AudioSystem.getClip();
                AudioInputStream audioInputStream = new AudioInputStream(
                        new ByteArrayInputStream(sound.audioData),
                        sound.format,
                        sound.audioData.length / sound.format.getFrameSize()
                );
                clip.open(audioInputStream);
                clip.start();
            } catch (LineUnavailableException | java.io.IOException e) {
                e.printStackTrace();
            }
        }
    }

    // Game Dimensions
    private static final int WIDTH = 800;
    private static final int HEIGHT = 600;
    private static final int PADDLE_WIDTH = 15;
    private static final int PADDLE_HEIGHT = 80;
    private static final int BALL_SIZE = 15;
    private static final int PADDLE_SPEED = 5;

    // Game State
    private final Rectangle player1, player2, ball;
    private int ballXSpeed = 3;
    private int ballYSpeed = 3;
    private int player1YDir = 0;
    private int player2YDir = 0;
    private int player1Score = 0;
    private int player2Score = 0;
    private boolean gameStarted = false;

    // Sounds
    private final List<SoundGenerator.Sound> sounds;
    private final SoundGenerator soundGenerator;

    public PongGame() {
        setPreferredSize(new Dimension(WIDTH, HEIGHT));
        setBackground(Color.BLACK);
        addKeyListener(this);
        setFocusable(true);

        // Initialize game objects
        player1 = new Rectangle(30, HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT);
        player2 = new Rectangle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT);
        ball = new Rectangle(WIDTH / 2 - BALL_SIZE / 2, HEIGHT / 2 - BALL_SIZE / 2, BALL_SIZE, BALL_SIZE);

        // Initialize sounds
        soundGenerator = new SoundGenerator();
        sounds = new ArrayList<>();
        sounds.add(soundGenerator.generateBeepSound("Hit", 440, 0.1));  // Paddle hit
        sounds.add(soundGenerator.generateBeepSound("Score", 523.25, 0.2)); // Scoring
        sounds.add(soundGenerator.generateBeepSound("Start", 659.25, 0.1)); // Game start

        // Start game thread
        new Thread(this).start();
    }

    private void resetBall() {
        ball.setLocation(WIDTH / 2 - BALL_SIZE / 2, HEIGHT / 2 - BALL_SIZE / 2);
        ballXSpeed = (ballXSpeed > 0 ? 3 : -3);
        ballYSpeed = (ballYSpeed > 0 ? 3 : -3);
    }

    private void move() {
        player1.y = Math.max(0, Math.min(player1.y + player1YDir, HEIGHT - PADDLE_HEIGHT));
        player2.y = Math.max(0, Math.min(player2.y + player2YDir, HEIGHT - PADDLE_HEIGHT));
        ball.x += ballXSpeed;
        ball.y += ballYSpeed;
    }

    private void checkCollision() {
        // Ball collision with top/bottom walls
        if (ball.y <= 0 || ball.y >= HEIGHT - BALL_SIZE) {
            ballYSpeed = -ballYSpeed;
        }

        // Ball collision with paddles
        if (ball.intersects(player1) || ball.intersects(player2)) {
            ballXSpeed = -ballXSpeed;
            soundGenerator.playSound(sounds.get(0)); // Play paddle hit sound
        }

        // Scoring
        if (ball.x < 0) {
            player2Score++;
            soundGenerator.playSound(sounds.get(1)); // Play scoring sound
            resetBall();
        } else if (ball.x > WIDTH) {
            player1Score++;
            soundGenerator.playSound(sounds.get(1)); // Play scoring sound
            resetBall();
        }
    }

    @Override
    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Draw background
        g2d.setColor(Color.BLACK);
        g2d.fillRect(0, 0, WIDTH, HEIGHT);

        // Draw paddles and ball
        g2d.setColor(Color.WHITE);
        g2d.fill(player1);
        g2d.fill(player2);
        g2d.fill(ball);

        // Draw scores
        g2d.setFont(new Font("Arial", Font.BOLD, 30));
        g2d.drawString(String.valueOf(player1Score), WIDTH / 2 - 50, 50);
        g2d.drawString(String.valueOf(player2Score), WIDTH / 2 + 30, 50);

        // Display start message
        if (!gameStarted) {
            g2d.setFont(new Font("Arial", Font.BOLD, 20));
            g2d.drawString("Press SPACE to start", WIDTH / 2 - 100, HEIGHT / 2);
        }
    }

    @Override
    public void run() {
        while (true) {
            if (gameStarted) {
                move();
                checkCollision();
            }
            repaint();

            try {
                Thread.sleep(16); // Approx. 60 FPS
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    @Override
    public void keyPressed(KeyEvent e) {
        if (e.getKeyCode() == KeyEvent.VK_SPACE) {
            if (!gameStarted) {
                soundGenerator.playSound(sounds.get(2)); // Play start sound
            }
            gameStarted = true;
        }

        // Player 1 controls
        if (e.getKeyCode() == KeyEvent.VK_W) {
            player1YDir = -PADDLE_SPEED;
        } else if (e.getKeyCode() == KeyEvent.VK_S) {
            player1YDir = PADDLE_SPEED;
        }

        // Player 2 controls
        if (e.getKeyCode() == KeyEvent.VK_UP) {
            player2YDir = -PADDLE_SPEED;
        } else if (e.getKeyCode() == KeyEvent.VK_DOWN) {
            player2YDir = PADDLE_SPEED;
        }
    }

    @Override
    public void keyReleased(KeyEvent e) {
        if (e.getKeyCode() == KeyEvent.VK_W || e.getKeyCode() == KeyEvent.VK_S) {
            player1YDir = 0;
        }
        if (e.getKeyCode() == KeyEvent.VK_UP || e.getKeyCode() == KeyEvent.VK_DOWN) {
            player2YDir = 0;
        }
    }

    @Override
    public void keyTyped(KeyEvent e) {
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Pong with Sound");
        PongGame pongGame = new PongGame();
        frame.add(pongGame);
        frame.pack();
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }
}
