import React, { useState, useEffect } from "react";
import axios from "axios";

const TodoApp = () => {
  const [todos, setTodos] = useState([]);
  const [newTitle, setNewTitle] = useState("");
  const [newDueDate, setNewDueDate] = useState("");
  const [isDone, setIsDone] = useState(false);
  const [editId, setEditId] = useState(null);

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      const response = await axios.get("http://localhost:8000/todos");
      setTodos(response.data);
    } catch (err) {
      console.error("Error fetching todos:", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Use current time if no due date is provided
    let dueDate = newDueDate ? new Date(newDueDate) : new Date();

    // Format the due date to include both date and time
    const formattedDueDate = dueDate.toISOString();

    try {
      if (editId) {
        await axios.put(`http://localhost:8000/todos/${editId}`, {
          task: newTitle,
          due_date: formattedDueDate,
          completed: isDone,
        });
      } else {
        await axios.post("http://localhost:8000/todos", {
          task: newTitle,
          due_date: formattedDueDate,
          completed: isDone,
        });
      }
      fetchTodos();
      setNewTitle("");
      setNewDueDate("");
      setIsDone(false);
      setEditId(null);
    } catch (err) {
      console.error("Error submitting todo:", err);
    }
  };

  const handleEdit = (todo) => {
    setNewTitle(todo.task);
    setNewDueDate(
      todo.due_date
        ? new Date(todo.due_date).toISOString().substring(0, 16)
        : ""
    );
    setIsDone(todo.completed);
    setEditId(todo.id);
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/todos/${id}`);
      fetchTodos();
    } catch (err) {
      console.error("Error deleting todo:", err);
    }
  };

  const formatDateTime = (dateTime) => {
    if (!dateTime) return "";
    const d = new Date(dateTime);
    return d.toLocaleString();
  };

  return (
    <div className="todo-container">
      <h2>Todo App</h2>
      <form onSubmit={handleSubmit} className="todo-form">
        <div>
          <label>Task:</label>
          <input
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Due Date:</label>
          <input
            type="datetime-local"
            value={newDueDate}
            onChange={(e) => setNewDueDate(e.target.value)}
          />
        </div>
        <div>
          <label>Completed:</label>
          <input
            type="checkbox"
            checked={isDone}
            onChange={(e) => setIsDone(e.target.checked)}
          />
        </div>
        <button type="submit">{editId ? "Update" : "Add"} Todo</button>
      </form>
      <div className="todo-list">
        {todos.map((todo) => (
          <div key={todo.id} className="todo-item">
            <p>Task: {todo.task}</p>
            <p>Due: {formatDateTime(todo.due_date)}</p>
            <p>Status: {todo.completed ? "Completed" : "Not completed"}</p>
            <button onClick={() => handleEdit(todo)}>Edit</button>
            <button onClick={() => handleDelete(todo.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TodoApp;
