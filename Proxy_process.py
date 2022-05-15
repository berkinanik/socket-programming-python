# import necessary libraries
import socket


# define global variables
requestIndices = list()
requestData = list()
responseIndices = list()
responseData = list()
serverRequestIndices = list()
serverRequestData = list()
serverResponseIndices = list()
serverResponseData = list()
summationResult = 0
clientMessage = ""
serverMessage = ""
serverResponseMessage = ""
serverConnectionNeeded = False
serverConnectionEstablished = False
# socket variables
HOST = "127.0.0.1"
SELF_PORT = 8081
SERVER_PORT = 8080
# connect to backend server
# define proxy server socket
try:
    proxyServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Proxy - server socket created successfully\n")
except Exception as e:
    print(str(e))
    print("Error occured while creating the proxy - server socket")
    exit(1)
try:
    proxyServerSocket.connect((HOST, SERVER_PORT))
    print("Connected to the backend server at {0}:{1}\n".format(HOST, SERVER_PORT))
except Exception as e:
    print(str(e))
    print("Error occured while connecting to the backend server")
    exit(1)
# define proxy client socket
try:
    proxyClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxyClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxyClientSocket.bind((HOST, SELF_PORT))
except Exception as e:
    print(str(e))
    print("Error occured while creating the client - proxy socket")
    exit(1)
print("Proxy server is running on {0}:{1}\n".format(HOST, SELF_PORT))
try:
    proxyClientSocket.listen(1)
    print("Listening for connections")
except Exception as e:
    print(str(e))
    print("Error occured while listening for connections")
    exit(1)
try:
    clientConnection, clientAddress = proxyClientSocket.accept()
    print("Connected by", clientAddress)
except Exception as e:
    print(str(e))
    print("Error occured while accepting the connection")
    exit(1)

# proxy server table
proxyStorageIndices = []
proxyStorageData = []

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
            elif key == "CODE":
                if int(value) == 404:
                    raise Exception("404-Requested indices not found. Try again")
                elif int(value) == 500:
                    raise Exception("505-Server error. Try again")
                elif int(value) == 200:
                    pass
    except Exception as e:
        raise e
    return operation


def send_message_to_client():
    global clientMessage
    global clientConnection
    try:
        clientConnection.send(clientMessage.encode("utf-8"))
        print("Sent message to client: {0}".format(clientMessage))
    except:
        print("Error occured while sending message to client")
        raise Exception("500-Error occured while sending message to client")


def send_message_to_server():
    global serverMessage
    global proxyServerSocket
    try:
        proxyServerSocket.send(serverMessage.encode("utf-8"))
        print("Sent message to server: {0}".format(serverMessage))
    except:
        print("Error occured while sending message to backend server")
        raise Exception("500-Error occured while sending message to backend server")


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
    global summationResult
    if operation == "GET":
        clientMessage = "OP=GET;IND={0};DATA={1};CODE=200".format(
            ",".join(str(i) for i in responseIndices), ",".join(str(i) for i in responseData)
        )
    elif operation == "PUT":
        clientMessage = "OP=PUT;IND={0};DATA={1};CODE=200".format(
            ",".join(str(i) for i in serverResponseIndices), ",".join(str(i) for i in serverResponseData)
        )
    elif operation == "CLR":
        clientMessage = "OP=CLR;CODE=200"
    elif operation == "ADD":
        clientMessage = "OP=ADD;IND={0};DATA={1};CODE=200".format(
            ",".join(str(i) for i in responseIndices), summationResult
        )


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
    global summationResult
    if operation == "GET":
        for index in requestIndices:
            if index in proxyStorageIndices:
                responseIndices.append(index)
                responseData.append(proxyStorageData[proxyStorageIndices.index(index)])
            else:
                serverConnectionNeeded = True
                serverRequestIndices.append(index)
    elif operation == "PUT":
        serverConnectionNeeded = True
        proxyTableUpdated = False
        # update the proxy table for existing indices
        for index in requestIndices:
            if index in proxyStorageIndices:
                proxyStorageData[proxyStorageIndices.index(index)] = requestData[requestIndices.index(index)]
                proxyTableUpdated = True
            serverRequestIndices.append(index)
            serverRequestData.append(requestData[requestIndices.index(index)])
        if proxyTableUpdated:
            print_proxy_table()
    elif operation == "CLR":
        serverConnectionNeeded = True
        # clear the proxy table
        proxyStorageData = []
        proxyStorageIndices = []
        lastUpdated = []
        print("Proxy table cleared\n")
    elif operation == "ADD":
        summation = 0
        for index in requestIndices:
            if index in proxyStorageIndices:
                summation += proxyStorageData[proxyStorageIndices.index(index)]
            else:
                serverConnectionNeeded = True
                break
        if serverConnectionNeeded:
            for index in requestIndices:
                serverRequestIndices.append(index)
        else:
            summationResult = summation
            responseIndices = requestIndices


def perform_server_response_operation(operation):
    global proxyStorageIndices
    global proxyStorageData
    global lastUpdated
    global serverResponseIndices
    global serverResponseData
    global summationResult
    global responseIndices
    global responseData
    if operation == "GET":
        for index in serverResponseIndices:
            responseIndices.append(index)
            responseData.append(serverResponseData[serverResponseIndices.index(index)])
            if len(proxyStorageData) == 5:
                proxyStorageIndices.pop(0)
                proxyStorageData.pop(0)
            proxyStorageIndices.append(index)
            proxyStorageData.append(serverResponseData[serverResponseIndices.index(index)])
        print_proxy_table()
    elif operation == "ADD":
        summationResult = serverResponseData[0]
        responseIndices = serverResponseIndices


# function to print proxy table
def print_proxy_table():
    print("\nChanges made to the proxy table:")
    print("Index\tData")
    for i in range(len(proxyStorageIndices)):
        print("{0}\t{1}".format(proxyStorageIndices[i], proxyStorageData[i]))
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
    global serverResponseMessage
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
    serverResponseMessage = ""
    serverConnectionNeeded = False
    serverConnectionEstablished = False


def main():
    global proxyClientSocket
    global clientConnection
    global clientAddress
    global serverConnectionNeeded
    global clientMessage
    while True:
        try:
            dataReceived = clientConnection.recv(1024)
        except:
            print(clientAddress, "disconnected")
            proxyClientSocket.listen(1)
            clientConnection, clientAddress = proxyClientSocket.accept()
            print("Connected by", clientAddress)
            continue
        if dataReceived:
            try:
                dataReceived = dataReceived.decode("utf-8")
            except:
                print("Error occured while decoding the message")
                clientMessage = "CODE=500"
                try:
                    send_message_to_client()
                except:
                    pass
                clear_variables()
                continue
            print("Received message from client: {0}".format(dataReceived))
            try:
                operation = decompose_message(dataReceived)
                perform_operation(operation)
                if serverConnectionNeeded:
                    prepare_server_message(operation)
                    send_message_to_server()
                    try:
                        serverDataReceived = proxyServerSocket.recv(1024)
                    except:
                        print("Error occurred while receiving data from the backend server.\n")
                        print("Exiting...\n")
                        exit(1)
                    if serverDataReceived:
                        try:
                            serverResponseMessage = serverDataReceived.decode("utf-8")
                        except:
                            print("Error occured while decoding the message")
                            continue
                        print("Received message from the backend server: {0}".format(serverResponseMessage))
                        operation = decompose_message(serverResponseMessage, True)
                        perform_server_response_operation(operation)
                prepare_client_message(operation)
                send_message_to_client()
                print("\n")
            except Exception as e:
                print(str(e))
                print("\n")
                if "404" in str(e):
                    clientMessage = "CODE=404"
                if "500" in str(e):
                    clientMessage = "CODE=500"
                try:
                    send_message_to_client()
                except:
                    pass
            clear_variables()


if __name__ == "__main__":
    main()
