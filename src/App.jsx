// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import TodoApp from "./components/TodoApp"; // Assuming TodoApp is the component for your todo app
import "./index.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/todo" element={<TodoApp />} />
      </Routes>
    </Router>
  );
}

export default App;
