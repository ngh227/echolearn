import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FaMicrophone, FaStop, FaFilePdf } from 'react-icons/fa';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css'; // Import styles
import './App.css'; // Import your CSS file for styling

const initialData = [
  { name: 'Trial 1', value: 50 },
  { name: 'Trial 2', value: 75 },
  { name: 'Trial 3', value: 60 },
  { name: 'Trial 4', value: 70 },
  { name: 'Final wk', value: 80 },
];

const mockQuestions = [
  "What is the function of the mitochondria in a cell?",
  "Explain the process of photosynthesis.",
  "Describe the stages of cell division.",
  "What is the difference between DNA and RNA?",
  "How do enzymes work in biological processes?",
  "What is the main role of carbohydrates in the human body?",
  "Explain the significance of the water cycle in nature.",
  "What are the different types of chemical bonds?",
  "How does the circulatory system function?",
  "What is Newton's third law of motion?",
  "According to the text, why was protein initially considered a more likely candidate for the genetic material than DNA?",
  "What is the function of ribosomes in a cell?",
  "How does osmosis differ from diffusion?",
  "Who discovered the structure of DNA and how did they achieve this?",
  "Describe the greenhouse effect.",
  "Who discovered the structure of DNA and how did they achieve this?",
  "Explain the role of insulin in the human body.",
  "What is the difference between prokaryotic and eukaryotic cells?",
  "How does human digestion work?",
  "What are the primary functions of the skeletal system?"
];

const getRandomQuestions = (questions, count) => {
  const shuffled = [...questions].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};

const StudyApp = () => {
  const [file, setFile] = useState(null);
  const [fileUrl, setFileUrl] = useState(''); // State to store file URL
  const [recording, setRecording] = useState(false);
  const [timer, setTimer] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [understanding, setUnderstanding] = useState(0);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [fileAnalysis, setFileAnalysis] = useState(false); // Track file analysis state
  const [chartData, setChartData] = useState(initialData); // State for chart data
  const [successful, setSuccessful] = useState(0); // Track successful questions
  const [unsuccessful, setUnsuccessful] = useState(0); // Track unsuccessful questions

  useEffect(() => {
    let interval;
    if (recording) {
      interval = setInterval(() => {
        setTimer((prevTimer) => prevTimer + 1);
      }, 1000);
    } else if (!recording && timer !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [recording, timer]);

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile && uploadedFile.type === 'application/pdf') {
      setFile(uploadedFile);
      setFileUrl(URL.createObjectURL(uploadedFile)); // Create URL for uploaded file
      alert('File uploaded successfully!');
      setFileUploaded(true);
      setFileAnalysis(true); // Start analyzing file
      setAnalyzing(false); // Ensure not analyzing speech when file is uploaded

      // Simulate file analysis
      setTimeout(() => {
        setFileAnalysis(false);
        const randomQuestions = getRandomQuestions(mockQuestions, 5); // Get 10 random questions
        setQuestions(randomQuestions); // Generate mock questions after analysis
      }, 3000); // 3 seconds delay for analysis
    } else {
      alert('Please upload a PDF file.');
    }
  };

  const handleRecordToggle = async () => {
    if (!fileUploaded) {
      alert('Please upload a study material first!');
      return;
    }

    if (!recording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('Microphone access granted');
        setRecording(true);
        setTimer(0);
        setUnderstanding(0);
        setSuccessful(0);
        setUnsuccessful(0);
        // You can handle the recording with stream object if needed
      } catch (err) {
        console.error('Microphone access denied:', err);
        alert('Please allow access to the microphone to start recording.');
      }
    } else {
      setRecording(false);
      setAnalyzing(true);
      // Calculate understanding score and successful/unsuccessful questions based on timer duration
      setTimeout(() => {
        setAnalyzing(false);
        // Calculate understanding score based on timer
        const calculatedUnderstanding = Math.min(100, (timer / 30) * 100); // Cap at 100%
        setUnderstanding(Math.floor(calculatedUnderstanding));

        // Calculate successful and unsuccessful based on time recorded
        const successfulQuestions = Math.floor(timer / 5);
        setSuccessful(successfulQuestions);
        setUnsuccessful(5 - successfulQuestions); // Assuming 10 questions total

        // Update the last entry in the bar chart with the new progress percentage
        setChartData((prevData) => {
          const newData = [...prevData];
          newData[newData.length - 1].value = calculatedUnderstanding; // Set the last week's value to the understanding score
          return newData;
        });
      }, 2000);
    }
  };
  return (
    <div className="app-container" style={{ backgroundColor: '#f9fafb', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Header Bar for App Name */}
      <header style={{ backgroundColor: '#48a157', padding: '16px', textAlign: 'center' }}>
      <h1 style={{ 
  color: 'white', 
  fontSize: '40px', 
  fontWeight: 'bold', 
  margin: '0', 
  fontFamily: "'Comic Sans MS', 'Comic Sans', cursive" 
}}>
          Echolearn
          
        </h1>
        

      </header>
  
      {/* Main Content Area */}
      <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto', backgroundColor: 'white', position: 'relative', flex: '1' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '16px', color: 'black' }}>Process Checker</h1>
        
        {/* Chart Section */}
        <div style={{ marginBottom: '24px', height: '300px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(tick) => `${tick}%`} /> {/* Y-Axis formatted to percentage */}
              <Tooltip formatter={(value) => `${value}%`} />
              <Bar dataKey="value" fill="#d152a4" /> {/* Main bar color updated */}
            </BarChart>
          </ResponsiveContainer>
        </div>
  
        {/* Understanding Checker and Upload Section */}
        <div style={{ display: 'grid', gridTemplateColumns: '10fr 10fr', gap: '50px', marginBottom: '24px' }}>
          <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '16px', textAlign: 'center' }}>
            <h2 style={{ fontSize: '18px', marginBottom: '8px', color: 'black' }}>Understanding Checking</h2>
            <div style={{ width: '150px', height: '150px', margin: '0 auto' }}>
              <CircularProgressbar
                value={understanding}
                text={`${understanding}%`}
                styles={buildStyles({
                  pathColor: '#48a157',
                  textColor: '#48a157',
                  trailColor: '#e0e0e0',
                  textSize: '18px',
                })}
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '16px' }}>
              <div>
                <p style={{ color: '#666' }}>{unsuccessful}</p>
                <p style={{ fontSize: '12px', color: '#666' }}>Unsuccessful</p>
              </div>
              <div>
                <p style={{ color: '#48a157' }}>{successful}</p>
                <p style={{ fontSize: '12px', color: '#666' }}>Question passed</p>
              </div>
            </div>
          </div>
  
          {/* Upload Section */}
          <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '16px' }}>
            <h2 style={{ fontSize: '18px', marginBottom: '8px', color: 'black' }}>Upload Study Material</h2>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100px', border: '2px dashed #ccc', borderRadius: '8px', cursor: 'pointer' }}>
              <label style={{ textAlign: 'center' }}>
                <span style={{ color: 'black' }}>Click to upload or drag and drop</span>
                <br />
                <span style={{ fontSize: '12px', color: '#666' }}>PDF (MAX. 10MB)</span>
                <input type="file" style={{ display: 'none' }} onChange={handleFileUpload} accept=".pdf" />
              </label>
            </div>
            {file && (
              <div style={{ marginTop: '16px', textAlign: 'center' }}>
                <FaFilePdf style={{ color: '#d152a4', marginRight: '8px' }} />
                <a href={fileUrl} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: '#007bff' }}>
                  {file.name}
                </a>
              </div>
            )}
          </div>
        </div>
  
        {fileAnalysis && <p style={{ textAlign: 'center', color: '#d152a4' }}>Analyzing file...</p>}
  
        {fileUploaded && !fileAnalysis && questions.length > 0 && (
          <div style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '18px', marginBottom: '8px', color: 'black' }}>Generated Questions</h2>
            <div style={{ display: 'flex', flexDirection: 'column' }}> {/* Changed to flex with column direction */}
              {questions.map((question, index) => (
                <p key={index} style={{ marginBottom: '8px', color: 'black' }}>{question}</p>
              ))}
            </div>
          </div>
        )}
  
        {/* Record Section */}
        <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '16px', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '18px', marginBottom: '8px', color: 'black' }}>Record Your Answer</h2>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              onClick={handleRecordToggle}
              style={{
                padding: '8px 16px',
                backgroundColor: recording ? '#d152a4' : '#48a157',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              {recording ? (
                <>
                  <FaStop style={{ marginRight: '8px' }} /> Stop Recording
                </>
              ) : (
                <>
                  <FaMicrophone style={{ marginRight: '8px' }} /> Start Recording
                </>
              )}
            </button>
            <span style={{ color: 'black' }}>{timer} seconds</span>
          </div>
          {analyzing && <p style={{ marginTop: '16px', color: '#d152a4' }}>Analyzing speech...</p>}
        </div>
      </div>
  
      {/* Footer for Copyright Notice */}
      <footer style={{ backgroundColor: '#d152a4', padding: '16px', textAlign: 'center', color: 'white' }}>
        <p style={{ margin: '0', fontSize: '14px' }}>© Nga Vu, Maeve Ho - Hackathon</p>
      </footer>
      <img src="/character.png" alt="Character" className="character-image" />
    </div>
  );
}


  export default StudyApp;