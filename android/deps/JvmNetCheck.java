// Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
// All Rights Reserved, Without Prejudice · CashApp $axoneme
// 93
//
// JvmNetCheck -- does this JVM have REAL TCP, or is the sandbox
// fake-connecting every Java socket?
//
// METHOD: connect to 127.0.0.1:9 (discard -- nothing listens). A real
//   TCP stack REFUSES (ConnectException -> exit 0: the JVM can do
//   real networking). The sandbox fake-ACCEPTS everything (exit 1:
//   JVM networking is intercepted -- Gradle can never resolve).
// No network traffic leaves the machine; the answer is in the refusal.

import java.net.ConnectException;
import java.net.InetSocketAddress;
import java.net.Socket;

public class JvmNetCheck {
    public static void main(String[] args) {
        try (Socket s = new Socket()) {
            s.connect(new InetSocketAddress("127.0.0.1", 9), 3000);
            System.out.println("INTERCEPTED: connect to a closed port "
                    + "'succeeded' -- JVM TCP is fake; Gradle cannot "
                    + "reach the network on this host.");
            System.exit(1);
        } catch (ConnectException e) {
            System.out.println("OK: JVM TCP is real (connection refused "
                    + "as expected on a closed port).");
            System.exit(0);
        } catch (Exception e) {
            System.out.println("UNKNOWN: " + e);
            System.exit(2);
        }
    }
}
