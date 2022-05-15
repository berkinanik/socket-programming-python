# import necessary libraries
import socket
from time import sleep


# define global variables
requestIndices = list()
requestData = list()
responseIndices = list()
responseData = list()
serverRequestIndices = list()
serverRequestData = list()
serverResponseIndices = list()
serverResponseData = list()
clientMessage = ""
serverMessage = ""
serverResponse = ""
serverConnectionNeeded = False
serverConnectionEstablished = False
# socket variables
HOST = "127.0.0.1"
SELF_PORT = 8081
SERVER_PORT = 8080
# define proxy server socket
try:
    proxyServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxyServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxyServerSocket.bind((HOST, SELF_PORT))
except:
    print("Error occured while creating the proxy server socket")
    exit(1)
print("Proxy server is running on {0}:{1}\n".format(HOST, SELF_PORT))
try:
    proxyServerSocket.listen(1)
    print("Listening for connections")
except:
    print("Error occured while listening for connections")
    exit(1)
try:
    clientConnection, clientAddress = proxyServerSocket.accept()
    print("Connected by", clientAddress)
except:
    print("Error occured while accepting the connection")
    exit(1)
# try:
#     proxyServerSocket.connect((HOST, SERVER_PORT))
#     print("Connected to the backend server at {0}:{1}\n".format(HOST, SERVER_PORT))
# except:
#     print("Error occured while connecting to the backend server")
#     exit(1)
# proxy server table
proxyStorageIndices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
proxyStorageData = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
lastRetrieved = []

# message format is:
# OP=<operation>;IND=<index1>,<index2>...;DATA=<data1>,<data2>...
# valid operations are: GET, PUT, CLR, ADD

# function to extract the operation, indices and data from the message
# and return the operation type
def decompose_message(message, isServerResponse=False):
    global requestIndices
    global requestData
    global serverResponseIndices
    global serverResponseData
    # split the message into parts
    operation = ""
    messageParts = message.split(";")
    try:
        for mPart in messageParts:
            key, value = mPart.split("=")
            # extract the operation
            if key == "OP":
                operation = value
            # extract the indices
            elif key == "IND":
                if isServerResponse:
                    serverResponseIndices = [int(i) for i in value.split(",")]
                else:
                    requestIndices = [int(i) for i in value.split(",")]
            # extract the data
            elif key == "DATA":
                if isServerResponse:
                    serverResponseData = [int(i) for i in value.split(",")]
                else:
                    requestData = [int(i) for i in value.split(",")]
    except:
        print("Error occured while decomposing the message")
        raise Exception("500-Error occured while decomposing the message")
    return operation


def send_message_to_client():
    global clientMessage
    try:
        clientConnection.send(clientMessage.encode("utf-8"))
        print("\nSent message to client: {0}".format(clientMessage))
    except:
        print("Error occured while sending message to client")
        raise Exception("500-Error occured while sending message to client")


def send_message_to_server():
    global serverMessage
    try:
        proxyServerSocket.send(serverMessage.encode("utf-8"))
    except:
        print("Error occured while sending message to client")
        raise Exception("500-Error occured while sending message to server")


def prepare_server_message(operation):
    global serverMessage
    global serverRequestIndices
    global serverRequestData
    if operation == "GET":
        serverMessage = "OP=GET;IND={0}".format(",".join(str(i) for i in serverRequestIndices))
    elif operation == "PUT":
        serverMessage = "OP=PUT;IND={0};DATA={1}".format(
            ",".join(str(i) for i in serverRequestIndices), ",".join(str(i) for i in serverRequestData)
        )
    elif operation == "CLR":
        serverMessage = "OP=CLR"
    elif operation == "ADD":
        serverMessage = "OP=ADD;IND={0}".format(",".join(str(i) for i in serverRequestIndices))


def prepare_client_message(operation):
    global clientMessage
    global responseIndices
    global responseData
    if operation == "GET":
        clientMessage = "OP=GET;IND={0};DATA={1};CODE=200".format(
            ",".join(str(i) for i in responseIndices), ",".join(str(i) for i in responseData)
        )
    elif operation == "PUT":
        pass
    elif operation == "CLR":
        clientMessage = "OP=CLR;CODE=200"
    elif operation == "ADD":
        pass


# function to update last retrieved list
def update_last_retrieved(index):
    global lastRetrieved
    if len(lastRetrieved) == 5:
        lastRetrieved.pop(0)
        lastRetrieved.append(index)
    else:
        lastRetrieved.append(index)


# function to perform required operation
def perform_operation(operation):
    global proxyStorageIndices
    global proxyStorageData
    global lastUpdated
    global requestIndices
    global requestData
    global responseIndices
    global responseData
    global serverConnectionNeeded
    if operation == "GET":
        for index in requestIndices:
            if index in proxyStorageIndices:
                responseIndices.append(index)
                responseData.append(proxyStorageData[proxyStorageIndices.index(index)])
                update_last_retrieved(index)
            else:
                serverConnectionNeeded = True
                serverRequestIndices.append(index)
    elif operation == "PUT":
        serverConnectionNeeded = True
        # update the proxy table for existing indices
        for index in requestIndices:
            if index in proxyStorageIndices:
                proxyStorageData[proxyStorageIndices.index(index)] = requestData[requestIndices.index(index)]
                update_last_retrieved(index)
            serverRequestIndices.append(index)
            serverRequestData.append(requestData[requestIndices.index(index)])
    elif operation == "CLR":
        serverConnectionNeeded = True
        # clear the proxy table
        proxyStorageData = []
        proxyStorageIndices = []
        lastUpdated = []
    elif operation == "ADD":
        serverConnectionNeeded = True
        for index in requestIndices:
            serverRequestIndices.append(index)


# function to print proxy table
def print_proxy_table():
    print("\nChanges made to the proxy table:")
    for i in range(len(proxyStorageIndices)):
        print("{0} {1}".format(proxyStorageIndices[i], proxyStorageData[i]))
    print("\n")


# function to clear variables
def clear_variables():
    global requestIndices
    global requestData
    global responseIndices
    global responseData
    global serverRequestIndices
    global serverRequestData
    global serverResponseIndices
    global serverResponseData
    global clientMessage
    global serverMessage
    global serverResponse
    global serverConnectionNeeded
    global serverConnectionEstablished
    requestIndices = []
    requestData = []
    responseIndices = []
    responseData = []
    serverRequestIndices = []
    serverRequestData = []
    serverResponseIndices = []
    serverResponseData = []
    clientMessage = ""
    serverMessage = ""
    serverResponse = ""
    serverConnectionNeeded = False
    serverConnectionEstablished = False


def main():
    global HOST
    global SELF_PORT
    global proxyServerSocket
    global clientConnection
    global clientAddress
    global serverConnectionNeeded
    while True:
        try:
            dataReceived = clientConnection.recv(1024)
        except:
            print(clientAddress, "disconnected")
            proxyServerSocket.listen(1)
            clientConnection, clientAddress = proxyServerSocket.accept()
            print("Connected by", clientAddress)
            sleep(0.5)
            continue
        if dataReceived:
            try:
                dataReceived = dataReceived.decode("utf-8")
            except Exception as e:
                print(str(e))
                try:
                    clientConnection.send("CODE=500".encode("utf-8"))
                except:
                    pass
                continue
            print("\nReceived message from client: {0}".format(dataReceived))
            try:
                operation = decompose_message(dataReceived)
                perform_operation(operation)
                if serverConnectionNeeded:
                    # send message to server
                    # wait for server response
                    # decompose the message
                    # update the proxy table
                    # add the response indicies and data to the response indices and data
                    pass
                prepare_client_message(operation)
                send_message_to_client()
                clear_variables()
                print("\n")
            except Exception as e:
                print(str(e))
                print("\n")
                if "404" in str(e):
                    try:
                        clientConnection.send("CODE=404".encode("utf-8"))
                    except:
                        pass
                if "500" in str(e):
                    try:
                        clientConnection.send("CODE=500".encode("utf-8"))
                    except:
                        pass


if __name__ == "__main__":
    main()
