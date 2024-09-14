const express = require('express');
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

// Create Express app
const app = express();
const port = 3000;  // Change port if necessary

// Middleware to parse JSON request bodies
app.use(express.json());

// MongoDB connection URI (Use your credentials)
const mongoURI = "mongodb+srv://dssmadhan:1234@mongo.ku9n0.mongodb.net/?retryWrites=true&w=majority&appName=MONGO";

// Connect to MongoDB
mongoose.connect(mongoURI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB Atlas'))
    .catch(err => console.log('Failed to connect to MongoDB Atlas:', err));

// Define User Schema and Model
const userSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    gesture: { type: String, required: true }
});

const User = mongoose.model('User', userSchema);

// Register Route (Signup)
app.post('/signup', async (req, res) => {
    const { username, gesture } = req.body;

    try {
        // Check if user already exists
        const existingUser = await User.findOne({ username });
        if (existingUser) return res.status(400).json({ msg: 'User already exists' });

        // Create new user
        const newUser = new User({
            username,
            gesture // Store the gesture directly
        });

        // Save user to the database
        await newUser.save();

        res.json({ msg: 'User registered successfully' });
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: 'Server error' });
    }
});

// Login Route
app.post('/login', async (req, res) => {
    const { username, gesture } = req.body;

    try {
        // Find the user by username
        const user = await User.findOne({ username });
        if (!user) return res.status(404).json({ msg: 'User not found' });

        // Check if the gesture matches
        if (user.gesture === gesture) {
            res.json({ msg: 'Login successful' });
        } else {
            res.status(401).json({ msg: 'Invalid credentials' });
        }
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: 'Server error' });
    }
});


// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
