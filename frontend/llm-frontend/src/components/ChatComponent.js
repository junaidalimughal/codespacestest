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
    if (inputValue.trim()) {
      try {
        // Replace 'YOUR_TEXT_ENDPOINT_URL' with your actual API endpoint for text messages
        const response = await axios.post('YOUR_TEXT_ENDPOINT_URL', { message: inputValue });
        setChatHistory([...chatHistory, response.data]);
        setInputValue(''); // Clear the input box after submission
      } catch (error) {
        setError(error);
      }
    }

    // Logic to send file
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        // Replace 'YOUR_FILE_ENDPOINT_URL' with your actual API endpoint for file uploads
        const response = await axios.post('YOUR_FILE_ENDPOINT_URL', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setChatHistory([...chatHistory, response.data]);
        setSelectedFile(null); // Clear the selected file after submission
      } catch (error) {
        setError(error);
      }
    }

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
      const response = await axios.post('YOUR_FILE_ENDPOINT_URL', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setChatHistory([...chatHistory, response.data]);
      setSelectedFile(null); // Clear the selected file after submission
    } catch (error) {
      setError(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  return (
    <div>
      <form onSubmit={handleSubmitFile}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload File</button>
      </form>
      <h1>Chat with us</h1>
      {isLoading && <p>Loading...</p>}
      {error && <p>Error: {error.message}</p>}
      <div className="chat-container">
        {chatHistory.map((message, index) => (
          <div key={index}>{message.text}</div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit}>
        <input
          class=".input-field"
          type="text"
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
