const express = require("express");
const mongoose = require("mongoose");

const app = express();

// Replace with your actual MongoDB connection string
const mongoURI = "mongodb+srv://dssmadhan:1234@mongo.ku9n0.mongodb.net/Login?retryWrites=true&w=majority&appName=MONGO/Login";

mongoose.connect(mongoURI)
    .then(() => console.log("MongoDB connected successfully"))
    .catch(err => console.log("MongoDB connection error:", err));

const userSchema = new mongoose.Schema({
    name: String,
    age: Number
});

const User = mongoose.model("User", userSchema);

const emp1 = new User({
    name: "Rijushree",
    age: 23
});

const saveEmployee = async () => {
    try {
        await emp1.save();
        console.log("Employee saved successfully");
    } catch (err) {
        console.log(err);
    }
};

saveEmployee();

app.listen(3001, () => {
    console.log("Server is running on port 3001");
});
