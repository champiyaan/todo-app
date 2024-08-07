import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
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
    } catch (error) {
      console.error("Error fetching todos:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (editId) {
      await updateTodo(editId);
    } else {
      await addTodo();
    }

    setNewTitle("");
    setNewDueDate("");
    setIsDone(false);
    setEditId(null);
    fetchTodos();
  };

  const addTodo = async () => {
    try {
      await axios.post("http://localhost:8000/todos", {
        task: newTitle,
        due_date: newDueDate || new Date().toISOString(),
        completed: isDone,
      });
    } catch (error) {
      console.error("Error adding todo:", error);
    }
  };

  const updateTodo = async (id) => {
    try {
      await axios.put(`http://localhost:8000/todos/${id}`, {
        task: newTitle,
        due_date: newDueDate || new Date().toISOString(),
        completed: isDone,
      });
    } catch (error) {
      console.error("Error updating todo:", error);
    }
  };

  const handleEdit = (todo) => {
    setNewTitle(todo.task);
    setNewDueDate(todo.created);
    setIsDone(todo.completed);
    setEditId(todo.id);
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/todos/${id}`);
      fetchTodos();
    } catch (error) {
      console.error("Error deleting todo:", error);
    }
  };

  return (
    <div className="todo-container">
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
        <button type="submit" className="addTodoButton">{editId ? "Update" : "Add"} Todo</button>
      </form>

      <div className="todo-list">
        {todos.map((todo) => (
          <div key={todo.id} className="todo-item">
            <span className={`task ${todo.completed ? "completed" : ""}`}>
              {todo.task} (Created: {new Date(todo.created).toLocaleString()})
            </span>
            <div className="actions">
              <button onClick={() => handleEdit(todo)}>✏️</button>
              <button onClick={() => handleDelete(todo.id)}>🗑️</button>
            </div>
          </div>
          
        ))}
      </div>
    </div>
  );
}

export default App;
