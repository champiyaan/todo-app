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
    const response = await axios.get("http://localhost:8000/todos");
    setTodos(response.data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newTodo = {
      task: newTitle,
      due_date: newDueDate || new Date().toISOString(),
      completed: isDone,
    };

    if (editId) {
      await axios.put(`http://localhost:8000/todos/${editId}`, newTodo);
    } else {
      await axios.post("http://localhost:8000/todos", newTodo);
    }
    setNewTitle("");
    setNewDueDate("");
    setIsDone(false);
    setEditId(null);
    fetchTodos();
  };

  const handleEdit = (todo) => {
    setNewTitle(todo.task);
    setNewDueDate(todo.due_date);
    setIsDone(todo.completed);
    setEditId(todo.id);
  };

  const handleDelete = async (id) => {
    await axios.delete(`http://localhost:8000/todos/${id}`);
    fetchTodos();
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
        <button type="submit">{editId ? "Update" : "Add"} Todo</button>
      </form>

      <div className="todo-list">
        {todos.map((todo) => (
          <div key={todo.id} className="todo-item">
            <span className={`task ${todo.completed ? "completed" : ""}`}>
              {todo.task} (Due: {new Date(todo.due_date).toLocaleString()})
            </span>
            <div className="actions">
              <button onClick={() => handleEdit(todo)}>✏️ Edit</button>
              <button onClick={() => handleDelete(todo)}>❌ Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TodoApp;
