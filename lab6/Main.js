import com.datastax.oss.driver.api.core.CqlSession;
import com.datastax.oss.driver.api.core.CqlSessionBuilder;
import com.datastax.oss.driver.api.core.cql.*;

import java.net.InetSocketAddress;
import java.time.Instant;
import java.time.LocalDate;

public class Main {

    private static final String KEYSPACE = "delivery_lab6";

    public static void main(String[] args) {

        try (CqlSession session = new CqlSessionBuilder()
                .addContactPoint(new InetSocketAddress("127.0.0.1", 9042))
                .withLocalDatacenter("datacenter1")
                .build()) {

            System.out.println("==========================================");
            System.out.println(" LABORATORY WORK #6 - DELIVERY SERVICE");
            System.out.println(" Cassandra Query-Driven Design");
            System.out.println("==========================================\n");

            // =========================================================
            // 1. KEYSPACE
            // =========================================================

            session.execute("""
                    CREATE KEYSPACE IF NOT EXISTS delivery_lab6
                    WITH replication = {
                        'class': 'SimpleStrategy',
                        'replication_factor': 1
                    }
                    """);

            session.execute("USE delivery_lab6");

            System.out.println("1. Keyspace created: delivery_lab6");


            // =========================================================
            // 2. DELETE OLD TABLES
            // =========================================================

            session.execute("DROP TABLE IF EXISTS orders_by_courier");
            session.execute("DROP TABLE IF EXISTS events_by_order");
            session.execute("DROP TABLE IF EXISTS orders_by_zone");


            // =========================================================
            // 3. TABLE: ORDERS BY COURIER
            // =========================================================

            session.execute("""
                    CREATE TABLE orders_by_courier (
                        courier_id text,
                        delivery_date date,
                        order_id text,
                        zone text,
                        customer_name text,
                        address text,
                        status text,
                        PRIMARY KEY ((courier_id), delivery_date, order_id)
                    )
                    WITH CLUSTERING ORDER BY (
                        delivery_date DESC,
                        order_id ASC
                    )
                    """);


            // =========================================================
            // 4. TABLE: EVENTS BY ORDER
            // =========================================================

            session.execute("""
                    CREATE TABLE events_by_order (
                        order_id text,
                        event_time timestamp,
                        event_id text,
                        courier_id text,
                        zone text,
                        status text,
                        description text,
                        PRIMARY KEY ((order_id), event_time, event_id)
                    )
                    WITH CLUSTERING ORDER BY (
                        event_time DESC,
                        event_id ASC
                    )
                    """);


            // =========================================================
            // 5. TABLE: ORDERS BY ZONE
            // =========================================================

            session.execute("""
                    CREATE TABLE orders_by_zone (
                        zone text,
                        delivery_date date,
                        order_id text,
                        courier_id text,
                        customer_name text,
                        status text,
                        PRIMARY KEY ((zone), delivery_date, order_id)
                    )
                    WITH CLUSTERING ORDER BY (
                        delivery_date DESC,
                        order_id ASC
                    )
                    """);

            System.out.println("2. Tables created successfully\n");


            // =========================================================
            // 6. INSERT DATA
            // =========================================================

            insertOrder(session,
                    "C001", "2026-10-01", "ORD001",
                    "CENTER", "Alice", "Abaya 10",
                    "DELIVERED");

            insertOrder(session,
                    "C001", "2026-10-02", "ORD002",
                    "CENTER", "Bob", "Dostyk 25",
                    "DELIVERED");

            insertOrder(session,
                    "C001", "2026-10-03", "ORD003",
                    "CENTER", "Charlie", "Auezov 15",
                    "IN_TRANSIT");

            insertOrder(session,
                    "C001", "2026-10-04", "ORD004",
                    "MEDEU", "David", "Furmanov 33",
                    "DELIVERED");

            insertOrder(session,
                    "C001", "2026-10-05", "ORD005",
                    "CENTER", "Emma", "Satpaev 18",
                    "DELIVERED");

            insertOrder(session,
                    "C001", "2026-10-06", "ORD006",
                    "BOSTANDYK", "Frank", "Navoi 44",
                    "IN_TRANSIT");

            insertOrder(session,
                    "C001", "2026-10-07", "ORD007",
                    "MEDEU", "Grace", "Kunaev 12",
                    "DELIVERED");

            insertOrder(session,
                    "C001", "2026-10-08", "ORD008",
                    "CENTER", "Helen", "Tole Bi 20",
                    "IN_TRANSIT");


            insertOrder(session,
                    "C002", "2026-10-01", "ORD009",
                    "BOSTANDYK", "Ivan", "Al-Farabi 10",
                    "DELIVERED");

            insertOrder(session,
                    "C002", "2026-10-02", "ORD010",
                    "MEDEU", "Jack", "Dostyk 45",
                    "DELIVERED");

            insertOrder(session,
                    "C002", "2026-10-03", "ORD011",
                    "CENTER", "Kate", "Abaya 55",
                    "IN_TRANSIT");

            insertOrder(session,
                    "C002", "2026-10-04", "ORD012",
                    "BOSTANDYK", "Leo", "Rozybakiev 22",
                    "DELIVERED");

            insertOrder(session,
                    "C002", "2026-10-05", "ORD013",
                    "MEDEU", "Maria", "Zheltoksan 30",
                    "DELIVERED");

            insertOrder(session,
                    "C002", "2026-10-06", "ORD014",
                    "CENTER", "Nick", "Furmanov 16",
                    "IN_TRANSIT");

            insertOrder(session,
                    "C002", "2026-10-07", "ORD015",
                    "BOSTANDYK", "Olga", "Gagarin 40",
                    "DELIVERED");

            insertOrder(session,
                    "C002", "2026-10-08", "ORD016",
                    "MEDEU", "Paul", "Kabanbay 12",
                    "IN_TRANSIT");


            insertOrder(session,
                    "C003", "2026-10-01", "ORD017",
                    "CENTER", "Quinn", "Abaya 70",
                    "DELIVERED");

            insertOrder(session,
                    "C003", "2026-10-02", "ORD018",
                    "MEDEU", "Rose", "Dostyk 80",
                    "DELIVERED");

            insertOrder(session,
                    "C003", "2026-10-03", "ORD019",
                    "BOSTANDYK", "Sam", "Navoi 50",
                    "IN_TRANSIT");

            insertOrder(session,
                    "C003", "2026-10-04", "ORD020",
                    "CENTER", "Tom", "Satpaev 40",
                    "DELIVERED");

            insertOrder(session,
                    "C003", "2026-10-05", "ORD021",
                    "MEDEU", "Uma", "Kunaev 20",
                    "DELIVERED");

            insertOrder(session,
                    "C003", "2026-10-06", "ORD022",
                    "BOSTANDYK", "Victor", "Al-Farabi 70",
                    "IN_TRANSIT");

            insertOrder(session,
                    "C003", "2026-10-07", "ORD023",
                    "CENTER", "Wendy", "Tole Bi 55",
                    "DELIVERED");

            insertOrder(session,
                    "C003", "2026-10-08", "ORD024",
                    "MEDEU", "Zack", "Dostyk 90",
                    "IN_TRANSIT");

            System.out.println("3. 24 orders inserted\n");


            // =========================================================
            // 7. EVENTS
            // =========================================================

            insertEvent(session, "ORD001", "2026-10-01T08:00:00Z",
                    "E001", "C001", "CENTER",
                    "Order created");

            insertEvent(session, "ORD001", "2026-10-01T10:00:00Z",
                    "E002", "C001", "CENTER",
                    "Courier picked up order");

            insertEvent(session, "ORD001", "2026-10-01T13:00:00Z",
                    "E003", "C001", "CENTER",
                    "Order delivered");


            insertEvent(session, "ORD002", "2026-10-02T08:30:00Z",
                    "E004", "C001", "CENTER",
                    "Order created");

            insertEvent(session, "ORD002", "2026-10-02T11:00:00Z",
                    "E005", "C001", "CENTER",
                    "Courier picked up order");

            insertEvent(session, "ORD002", "2026-10-02T14:00:00Z",
                    "E006", "C001", "CENTER",
                    "Order delivered");


            insertEvent(session, "ORD003", "2026-10-03T09:00:00Z",
                    "E007", "C001", "CENTER",
                    "Order created");

            insertEvent(session, "ORD003", "2026-10-03T12:00:00Z",
                    "E008", "C001", "CENTER",
                    "Courier picked up order");

            insertEvent(session, "ORD003", "2026-10-03T15:00:00Z",
                    "E009", "C001", "CENTER",
                    "Courier is delivering");


            insertEvent(session, "ORD009", "2026-10-01T08:00:00Z",
                    "E010", "C002", "BOSTANDYK",
                    "Order created");

            insertEvent(session, "ORD009", "2026-10-01T12:00:00Z",
                    "E011", "C002", "BOSTANDYK",
                    "Order delivered");


            insertEvent(session, "ORD017", "2026-10-01T09:00:00Z",
                    "E012", "C003", "CENTER",
                    "Order created");

            insertEvent(session, "ORD017", "2026-10-01T13:00:00Z",
                    "E013", "C003", "CENTER",
                    "Order delivered");

            System.out.println("4. Events inserted\n");


            // =========================================================
            // 8. Q1 - ORDERS BY COURIER
            // =========================================================

            System.out.println("==========================================");
            System.out.println("Q1. ORDERS OF COURIER C001");
            System.out.println("==========================================");

            ResultSet result = session.execute("""
                    SELECT *
                    FROM orders_by_courier
                    WHERE courier_id = 'C001'
                    """);

            printOrders(result);


            // =========================================================
            // 9. Q2 - ORDERS BY COURIER FOR PERIOD
            // =========================================================

            System.out.println("\n==========================================");
            System.out.println("Q2. ORDERS OF C001 FOR PERIOD");
            System.out.println("==========================================");

            result = session.execute("""
                    SELECT *
                    FROM orders_by_courier
                    WHERE courier_id = 'C001'
                    AND delivery_date >= '2026-10-03'
                    AND delivery_date <= '2026-10-06'
                    """);

            printOrders(result);


            // =========================================================
            // 10. Q3 - EVENTS OF ORDER
            // =========================================================

            System.out.println("\n==========================================");
            System.out.println("Q3. EVENTS OF ORDER ORD001");
            System.out.println("==========================================");

            result = session.execute("""
                    SELECT *
                    FROM events_by_order
                    WHERE order_id = 'ORD001'
                    """);

            printEvents(result);


            // =========================================================
            // 11. Q4 - ORDERS BY ZONE
            // =========================================================

            System.out.println("\n==========================================");
            System.out.println("Q4. ORDERS IN CENTER ZONE");
            System.out.println("==========================================");

            result = session.execute("""
                    SELECT *
                    FROM orders_by_zone
                    WHERE zone = 'CENTER'
                    """);

            printZoneOrders(result);


            // =========================================================
            // 12. Q5 - RECENT EVENTS
            // =========================================================

            System.out.println("\n==========================================");
            System.out.println("Q5. LAST EVENTS OF ORD003");
            System.out.println("==========================================");

            result = session.execute("""
                    SELECT *
                    FROM events_by_order
                    WHERE order_id = 'ORD003'
                    LIMIT 2
                    """);

            printEvents(result);


            // =========================================================
            // 13. UPDATE
            // =========================================================

            System.out.println("\n==========================================");
            System.out.println("UPDATE ORDER");
            System.out.println("==========================================");

            session.execute("""
                    UPDATE orders_by_courier
                    SET status = 'DELIVERED'
                    WHERE courier_id = 'C001'
                    AND delivery_date = '2026-10-03'
                    AND order_id = 'ORD003'
                    """);

            session.execute("""
                    UPDATE orders_by_zone
                    SET status = 'DELIVERED'
                    WHERE zone = 'CENTER'
                    AND delivery_date = '2026-10-03'
                    AND order_id = 'ORD003'
                    """);

            System.out.println("ORD003 status changed to DELIVERED");


            result = session.execute("""
                    SELECT *
                    FROM orders_by_courier
                    WHERE courier_id = 'C001'
                    AND delivery_date = '2026-10-03'
                    AND order_id = 'ORD003'
                    """);

            printOrders(result);


            // =========================================================
            // 14. DELETE
            // =========================================================

            System.out.println("\n==========================================");
            System.out.println("DELETE ORDER");
            System.out.println("==========================================");

            session.execute("""
                    DELETE FROM orders_by_courier
                    WHERE courier_id = 'C003'
                    AND delivery_date = '2026-10-08'
                    AND order_id = 'ORD024'
                    """);

            session.execute("""
                    DELETE FROM orders_by_zone
                    WHERE zone = 'MEDEU'
                    AND delivery_date = '2026-10-08'
                    AND order_id = 'ORD024'
                    """);

            System.out.println("ORD024 deleted");


            // =========================================================
            // 15. ANALYTICAL CALCULATION
            // =========================================================

            System.out.println("\n==========================================");
            System.out.println("ANALYTICAL CALCULATION");
            System.out.println("==========================================");

            result = session.execute("""
                    SELECT status
                    FROM orders_by_courier
                    WHERE courier_id = 'C001'
                    """);

            int delivered = 0;
            int inTransit = 0;

            for (Row row : result) {

                String status = row.getString("status");

                if ("DELIVERED".equals(status)) {
                    delivered++;
                }

                if ("IN_TRANSIT".equals(status)) {
                    inTransit++;
                }
            }

            int total = delivered + inTransit;

            System.out.println("Courier: C001");
            System.out.println("Total orders: " + total);
            System.out.println("Delivered: " + delivered);
            System.out.println("In transit: " + inTransit);

            if (total > 0) {
                double percentage =
                        delivered * 100.0 / total;

                System.out.printf(
                        "Delivery rate: %.2f%%%n",
                        percentage
                );
            }


            // =========================================================
            // 16. PARTITION ANALYSIS
            // =========================================================

            System.out.println("\n==========================================");
            System.out.println("PARTITION ANALYSIS");
            System.out.println("==========================================");

            System.out.println("""
                    orders_by_courier:
                    partition key = courier_id

                    C001 -> approximately 8 rows
                    C002 -> approximately 8 rows
                    C003 -> approximately 7 rows after DELETE

                    events_by_order:
                    partition key = order_id

                    One order normally contains several events.

                    orders_by_zone:
                    partition key = zone

                    CENTER, MEDEU and BOSTANDYK are separate partitions.
                    """);


            // =========================================================
            // 17. DESCRIBE-LIKE INFORMATION
            // =========================================================

            System.out.println("==========================================");
            System.out.println("LABORATORY WORK COMPLETED");
            System.out.println("==========================================");

            System.out.println("""
                    
                    Query-driven model:

                    Q1 -> orders_by_courier
                    Q2 -> orders_by_courier
                    Q3 -> events_by_order
                    Q4 -> orders_by_zone
                    Q5 -> events_by_order

                    No ALLOW FILTERING was used.

                    Data is intentionally duplicated between tables
                    because Cassandra uses denormalization to make
                    required reads predictable and fast.
                    """);

        } catch (Exception e) {

            System.err.println("\nERROR:");
            e.printStackTrace();
        }
    }


    // =============================================================
    // INSERT ORDER
    // =============================================================

    private static void insertOrder(
            CqlSession session,
            String courierId,
            String date,
            String orderId,
            String zone,
            String customer,
            String address,
            String status) {

        session.execute(
                SimpleStatement.newInstance(
                        """
                        INSERT INTO orders_by_courier
                        (courier_id, delivery_date, order_id,
                         zone, customer_name, address, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        courierId,
                        LocalDate.parse(date),
                        orderId,
                        zone,
                        customer,
                        address,
                        status
                )
        );

        session.execute(
                SimpleStatement.newInstance(
                        """
                        INSERT INTO orders_by_zone
                        (zone, delivery_date, order_id,
                         courier_id, customer_name, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        zone,
                        LocalDate.parse(date),
                        orderId,
                        courierId,
                        customer,
                        status
                )
        );
    }


    // =============================================================
    // INSERT EVENT
    // =============================================================

    private static void insertEvent(
            CqlSession session,
            String orderId,
            String time,
            String eventId,
            String courierId,
            String zone,
            String status) {

        session.execute(
                SimpleStatement.newInstance(
                        """
                        INSERT INTO events_by_order
                        (order_id, event_time, event_id,
                         courier_id, zone, status, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        orderId,
                        Instant.parse(time),
                        eventId,
                        courierId,
                        zone,
                        status,
                        status
                )
        );
    }


    // =============================================================
    // PRINT ORDERS
    // =============================================================

    private static void printOrders(ResultSet result) {

        for (Row row : result) {

            System.out.printf(
                    "Date: %s | Order: %s | Courier: %s | Zone: %s | Customer: %s | Status: %s%n",
                    row.getLocalDate("delivery_date"),
                    row.getString("order_id"),
                    row.getString("courier_id"),
                    row.getString("zone"),
                    row.getString("customer_name"),
                    row.getString("status")
            );
        }
    }


    // =============================================================
    // PRINT EVENTS
    // =============================================================

    private static void printEvents(ResultSet result) {

        for (Row row : result) {

            System.out.printf(
                    "Time: %s | Event: %s | Courier: %s | Zone: %s | Status: %s%n",
                    row.getInstant("event_time"),
                    row.getString("event_id"),
                    row.getString("courier_id"),
                    row.getString("zone"),
                    row.getString("status")
            );
        }
    }


    // =============================================================
    // PRINT ZONE ORDERS
    // =============================================================

    private static void printZoneOrders(ResultSet result) {

        for (Row row : result) {

            System.out.printf(
                    "Date: %s | Order: %s | Courier: %s | Customer: %s | Status: %s%n",
                    row.getLocalDate("delivery_date"),
                    row.getString("order_id"),
                    row.getString("courier_id"),
                    row.getString("customer_name"),
                    row.getString("status")
            );
        }
    }
}
