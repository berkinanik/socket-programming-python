# import necessary libraries
import socket
from time import sleep


# define global variables
requestIndices = list()
requestData = list()
serverMessage = ""
responseIndices = list()
responseData = list()
clientMessage = ""
# socket variables
HOST = "127.0.0.1"
SELF_PORT = 8081

# message format is:
# OP=<operation>;IND=<index1>,<index2>...;DATA=<data1>,<data2>...
# valid operations are: GET, PUT, CLR, ADD

# function to extract the operation, indices and data from the message
# and return the operation type
def decompose_message(message):
    global requestIndices
    global requestData
    # split the message into parts
    messageParts = message.split(";")
    # extract the operation
    operation = messageParts[0].split("=")[1]
    # extract the indices
    indices = [int(i) for i in messageParts[1].split("=")[1].split(",")]
    # extract the data
    data = [int(i) for i in messageParts[2].split("=")[1].split(",")]
    # store the extracted data in the global variables
    requestIndices = indices
    requestData = data
    return operation


# function to perform required operation
def perform_operation(operation):
    if operation == "GET":
        pass
    elif operation == "PUT":
        pass
    elif operation == "CLR":
        pass
    elif operation == "ADD":
        pass


def main():
    global HOST
    global SELF_PORT
    # define proxy server socket
    try:
        proxyServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxyServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxyServerSocket.bind((HOST, SELF_PORT))
    except:
        print("Error occured while creating the proxy server socket")
        exit(1)
    print("Proxy server is running on {0}:{1}\n".format(HOST, SELF_PORT))
    proxyServerSocket.listen(1)
    print("Listening for connections")
    conn, clientAddress = proxyServerSocket.accept()
    print("Connected by", clientAddress)
    while True:
        try:
            dataReceived = conn.recv(1024)
        except:
            print(clientAddress, "disconnected")
            proxyServerSocket.listen(1)
            conn, clientAddress = proxyServerSocket.accept()
            print("Connected by", clientAddress)
            sleep(0.5)
            continue
        if dataReceived:
            try:
                dataReceived = dataReceived.decode("utf-8")
            except:
                print("Error occured while decoding the message")
                continue
            print("\nReceived message from client: {0}".format(dataReceived))
            operation = decompose_message(dataReceived)


if __name__ == "__main__":
    main()
