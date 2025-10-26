import { useState, useEffect } from 'react';
import './App.css';

// The API_BASE_URL is your backend.
const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  // State for the list of tasks
  const [tasks, setTasks] = useState([]);

  // State for the text in the "new task" input field
  const [newTaskTitle, setNewTaskTitle] = useState("");

  // --- 1. FETCH ALL TASKS (GET) ---
  // We'll move the fetch logic into its own function
  // so we can call it whenever we want.
  async function fetchTasks() {
    const response = await fetch(`${API_BASE_URL}/tasks`);
    const data = await response.json();
    setTasks(data);
  }

  // useEffect still runs once on page load to get initial tasks
  useEffect(() => {
    fetchTasks();
  }, []);

  // --- 2. CREATE A NEW TASK (POST) ---
  async function handleSubmit(event) {
    // Prevent the browser from doing a full page refresh
    event.preventDefault(); 

    // Send the POST request
    await fetch(`${API_BASE_URL}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: newTaskTitle,
        completed: false
      })
    });

    // Clear the input field
    setNewTaskTitle("");

    // Refresh the task list to show the new task
    fetchTasks(); 
  }

  // --- 3. DELETE A TASK (DELETE) ---
  async function handleDelete(taskId) {
    await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
      method: "DELETE"
    });

    // Refresh the task list to show the task is gone
    fetchTasks(); 
  }

  // --- 4. THE HTML (JSX) ---
  return (
    <div className="App">
      <h1>My Task List</h1>

      {/* New Task Form */}
      <form onSubmit={handleSubmit} className="task-form">
        <input 
          type="text" 
          value={newTaskTitle}
          onChange={e => setNewTaskTitle(e.target.value)}
          placeholder="Add a new task"
        />
        <button type="submit">Add Task</button>
      </form>

      {/* Task List */}
      <ul className="task-list">
        {tasks.map(task => (
          <li key={task.id}>
            {task.title}
            <button 
              onClick={() => handleDelete(task.id)} 
              className="delete-button"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;