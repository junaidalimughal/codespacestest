import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Chat.css'; // Import your CSS file

function ChatComponent() {
  // ... (State and handleSubmit from previous example) ...
  const messagesEndRef = useRef(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState(''); // Added state for the input value
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null); // State to hold the selected file

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);

    // Logic to send text input

    try {
      // Replace 'YOUR_TEXT_ENDPOINT_URL' with your actual API endpoint for text messages
      console.log("calling the method.")
      const fileName = selectedFile ? selectedFile.name : ''
      console.log(inputValue)
      console.log(fileName)
      
      console.log("chat history length is");
      console.log(chatHistory.length)
      setChatHistory(prevChatHistory => [...prevChatHistory, {text: inputValue, textType: "user"}]);

      const response = await axios.post('http://127.0.0.1:8000/api/processllm/', { message: inputValue, fileName: fileName});
      console.log(response)
      setChatHistory(prevChatHistory => [...prevChatHistory, {text: response.data.message, df: response.data.df, textType: "System"}]);
      setInputValue(''); // Clear the input box after submission
      
      console.log("Chat history is -=> ")
      console.log(chatHistory);
    } catch (error) {
      setError(error);
    }
    
    /*
    // Logic to send file
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        // Replace 'YOUR_FILE_ENDPOINT_URL' with your actual API endpoint for file uploads
        const response = await axios.post('127.0.0.1:8000/api/processllm/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setChatHistory([...chatHistory, response.data]);
        setSelectedFile(null); // Clear the selected file after submission
      } catch (error) {
        setError(error);
      }
    }*/

    setIsLoading(false);
  };

  const handleSubmitFile = async (event) => {
    event.preventDefault();
    if (!selectedFile) return; // Early return if no file is selected
    setIsLoading(true);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Replace 'YOUR_FILE_ENDPOINT_URL' with your actual API endpoint
      const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      //setChatHistory([...chatHistory, response.data]);
      //setSelectedFile(null); // Clear the selected file after submission
    } catch (error) {
      setError(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleApiResponse = (response) => {
    // Assuming `response` is the object you received from your API
    const dfData = JSON.parse(response.df);
    
    // Construct a table from `dfData`
    const table = (
      <table className="styled-table">
        <thead>
          <tr>
            {dfData.columns.map((col, index) => (
              <th key={index}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dfData.data.map((row, index) => (
            <tr key={index}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
    
    // Set this table to state or use it directly in render as needed
    return table;
  };

  return (
    <div class="top-div">
      <form onSubmit={handleSubmitFile}>
        <input class="fileform" id="fileformfield" type="file" onChange={handleFileChange}/>
        <button id="fileformbutton" type="submit">Upload File</button>
      </form>
      <div class="chat-text">
        <h1>Chat with us</h1>
      </div>
      {isLoading && <p>Loading...</p>}
      {error && <p>Error: {error.message}</p>}
      <div className="chat-container">
        {chatHistory.length > 0 ? (
          chatHistory.map((message, index) => 
          <div key={index}>
              {message.textType == "user" ? <p>USER: {message.text}</p> : 

                <div class="chat-interaction">
                  <div>
                    <p>Response: </p>
                    <a href={message.text}>Download Analysis File</a>
                    {message.df && handleApiResponse(message)} {/* Render the table here if `df` exists */}

                  </div>
                </div>
              } 
            
          </div>)
          ) : (
              <p>No messages yet</p>
        )}        
      </div>
      
      <h4>Write a Python program to calculate .... </h4>
      <form class="fieldform" onSubmit={handleSubmit}>
        <input
          class="input-field"
          type="text"
          id="prompt"
          value={inputValue}
          onChange={handleInputChange}
          placeholder="Type your message here..."
        />
        <button type="submit">Send Message</button>
      </form>
    </div>
  );

}

export default ChatComponent;
