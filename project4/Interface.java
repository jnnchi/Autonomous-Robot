import javax.swing.*;
import java.awt.event.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;

/* --------------INTERFACE CLASS---------------- */
class Main {
  public static void main(String[] args)
  {
    /* --------------FRAME AND CLIENT---------------- */
    // creates frame and sets size and location
    JFrame frame = new JFrame();
    frame.setSize(700, 900);
    frame.setLocation(5,5);
    frame.setLayout(null);
    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

    // creates object of client class we wrote
    OurClient c = new OurClient();

    /* --------------BUTTONS---------------- */
    // creates the 5 buttons, sets position using: setBounds(x axis, y axis, width, height)
    JButton fwdB = new JButton("FWD");
    fwdB.setBounds(300, 50, 100, 100);
    JButton bwdB = new JButton("BWD");
    bwdB.setBounds(300, 550, 100, 100);
    JButton rightB = new JButton("RIGHT");
    rightB.setBounds(550, 300, 100, 100);
    JButton leftB = new JButton("LEFT");
    leftB.setBounds(50, 300, 100, 100);
    JButton autoB = new JButton("AUTO");
    autoB.setBounds(100, 700, 500, 100);

    /* --------------PANEL---------------- */
    // creates label and text field within a panel
    JLabel distLabel = new JLabel();
    distLabel.setText("<html><body>Input distance in ft or<br>angle in degrees:</body></html>");
    JPanel panel = new JPanel();
    panel.setBounds(250, 300, 200, 100);
    panel.add(distLabel);
    frame.add(panel);
    // creates input field with a width of 5 columns
    final JTextField input = new JTextField(5);
    panel.add(input);
    // creates label for the output
    final JLabel output = new JLabel();
    panel.add(output);

    /* --------------ADD TO FRAME---------------- */
    frame.add(fwdB);
    frame.add(bwdB);
    frame.add(rightB);
    frame.add(leftB);
    frame.add(autoB);
    frame.setVisible(true);

    /* --------------BUTTON ACTIONS---------------- */
    // The action listener which notices when the button is pressed
    // FORWARD BUTTON
    fwdB.addActionListener(new ActionListener()
    {
        public void actionPerformed(ActionEvent e)
        {
            String inputText = input.getText();

            try
            {
                int distance = Integer.parseInt(inputText);
                output.setText("Moving forward " + distance + " feet!");
                c.Forward(distance);
            }
            // exception if user does not input a number
            catch(Exception NumberFormatException)
            {
              int distance = 1;
              output.setText("<html><body>Moving forward<br>the default<br>1 foot!</html></body>");
              c.Forward(distance);
            }
        }
    });

    // BACKWARD BUTTON
    bwdB.addActionListener(new ActionListener()
    {
        public void actionPerformed(ActionEvent e)
        {
            String inputText = input.getText();

            try
            {
                int distance = Integer.parseInt(inputText);
                output.setText("Moving backward " + distance + " feet!");
                c.Backward(distance);
            }
            catch(Exception NumberFormatException)
            {
              int distance = 1;
              output.setText("<html><body>Moving backward<br>the default<br>1 foot!</html></body>");
              c.Backward(distance);
            }
        }
    });

    // RIGHT BUTTON
    rightB.addActionListener(new ActionListener()
    {
        public void actionPerformed(ActionEvent e)
        {
            String inputText = input.getText();

            try
            {
                int turnAngle = Integer.parseInt(inputText);
                output.setText("Turning right " + turnAngle + " degrees!");
                c.Right(turnAngle);
            }
            catch(Exception NumberFormatException)
            {
              int turnAngle = 90;
              output.setText("<html><body>Turning right<br>the default<br>90 degrees!</html></body>");
              c.Right(turnAngle);
            }
        }
    });

    // LEFT BUTTON
    leftB.addActionListener(new ActionListener()
    {
        public void actionPerformed(ActionEvent e)
        {
            String inputText = input.getText();

            try
            {
                int turnAngle = Integer.parseInt(inputText);
                output.setText("Turning left " + turnAngle + " degrees!");
                c.Left(turnAngle);
            }
            catch(Exception NumberFormatException)
            {
              int turnAngle = 90;
              output.setText("<html><body>Turning left<br>the default<br>90 degrees!</html></body>");
              c.Left(turnAngle);
            }
        }
    });

    // AUTO BUTTON
    autoB.addActionListener(new ActionListener()
    {
        public void actionPerformed(ActionEvent e)
        {
            output.setText("Running the default maze!");
            c.Auto();
        }
    });
  }
}


/* --------------CLIENT CLASS---------------- */
// every Java class has an Object superclass (inherits from it)
class OurClient extends Object
{
  public static void main(String[] args)
  {
    System.out.println("hi");
  }
  public int Forward(int distFWD)
  {
    System.out.println(distFWD);

    HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_2).build();

    // creates string verson of inputted distance, concatenates into URL
    String strDist = String.valueOf(distFWD);
    String fwdURL = "http://192.168.1.243:7777/fwd?d=" + strDist;
    // now creates request
    HttpRequest httpReq = HttpRequest.newBuilder().uri(URI.create(fwdURL)).build();

    // sendAsync(http request, body handler) sends the request and receives the response asynchronously
    httpClient.sendAsync(httpReq, BodyHandlers.ofString()).thenApply(HttpResponse::body).thenAccept(System.out::println);
    return 200;
  }

  public int Backward(int distBWD)
  {
    System.out.println(distBWD);

    HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_2).build();

    String strDist = String.valueOf(distBWD);
    String bwdURL = "http://192.168.1.243:7777/bwd?d=" + strDist;

    HttpRequest httpReq = HttpRequest.newBuilder().uri(URI.create(bwdURL)).build();
    httpClient.sendAsync(httpReq, BodyHandlers.ofString()).thenApply(HttpResponse::body).thenAccept(System.out::println);
    return 200;
  }

  public int Left(int angleL)
  {
    System.out.println(angleL);

    HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_2).build();

    String strAng = String.valueOf(angleL);
    String leftURL = "http://192.168.1.243:7777/left?a=" + strAng;

    HttpRequest httpReq = HttpRequest.newBuilder().uri(URI.create(leftURL)).build();
    httpClient.sendAsync(httpReq, BodyHandlers.ofString()).thenApply(HttpResponse::body).thenAccept(System.out::println);
    return 200;
  }

  public int Right(int angleR)
  {
    System.out.println(angleR);

    HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_2).build();

    String strAng = String.valueOf(angleR);
    String rightURL = "http://192.168.1.243:7777/right?a=" + strAng;

    HttpRequest httpReq = HttpRequest.newBuilder().uri(URI.create(rightURL)).build();
    httpClient.sendAsync(httpReq, BodyHandlers.ofString()).thenApply(HttpResponse::body).thenAccept(System.out::println);
    return 200;
  }

  public int Auto()
  {
    HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_2).build();
    HttpRequest httpReq = HttpRequest.newBuilder().uri(URI.create("http://192.168.1.243:7777/run")).build();
    httpClient.sendAsync(httpReq, BodyHandlers.ofString()).thenApply(HttpResponse::body).thenAccept(System.out::println);
    return 200;
  }
}

