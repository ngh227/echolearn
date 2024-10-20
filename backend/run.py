from app import app

if __name__ == '__main__':
    # Enable debug mode for development
    app.run(debug=True, host="0.0.0.0", port=5000)
