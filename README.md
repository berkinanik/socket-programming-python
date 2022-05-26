# socket-programming-python
This is a repository for my computer networks course assignment 1, I completed during the course of METU EE444 Introduction to Computer Networks in 2021-2022 Spring Semester.

*This assignment's instructions credit to [**Middle East Technical University - Electrical - Electronics Engineering Department**](https://eee.metu.edu.tr/) and [**METU EE444 Introduction to Computer Networks Course Lecturers**](https://catalog.metu.edu.tr/course.php?course_code=5670444).*

# Assignment Instructions
## **METU EE444 Introduction to Computer Networks**
### **HW1 - Socket Programming**

![](/images/image1.png)
> Figure 1 - Layered Network Architecture

![](/images/image2.png)
> Figure 2 - State Diagram of TCP Sockets

## Assignment Description
For this homework, you will implement a simple system consisting of 3 nodes. Namely,
Client, Proxy and Server. Topology is very simple and can be seen in Figure 3.

![](/images/image3.png)
> Figure 3 - Topology of the Network

### Operation Specifications
The Server will hold a list of 10 elements as described in Table 1. Each entry will consist
of an index value ranging from 0 to 9 and data of a single integer. The Proxy should be
consistent with the server, that is any update made to the Proxy's table should also be
made in Server's table.

![](/images/table1.png)

The Proxy server will hold half of the table in its process as described in Table 2,
think of it as a cached version of the Server's table. The Client will only communicate
with the proxy server, if an element that is not present in the Proxy's table is required
proxy server will communicate with the Server to get that element and add it to its table
by overwriting the oldest table entry.

![](/images/table2.png)

Nodes will exchange proxy messages between them with the format as below.

``OP=XXX;IND=Ind1,Ind2,..;DATA=Dat1,Dat2,...;``

Notice that fields are separated with semicolons(;). OP field describes which operation
to do on the table, for more detail check Table 3. IND field tells which of the indexes are
required for the operation. The DATA field is for integer data either from the server for
operations like "ADD" or as an update value from the client. Not all messages require
every field. You can choose to omit the unused fields for certain operations. Details of
the implementation are up to you.

Response messages have the same form as request messages. For example response
of the "ADD" message will have "ADD" as the operation code and contain the result in
the "DATA" field.

![](/images/table3.png)