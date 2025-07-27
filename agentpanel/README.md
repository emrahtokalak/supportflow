# ABCX Agent Panel

Modern web interface for interacting with the ABCX Customer Service AI Assistant.

## Features

- **Real-time Chat Interface**: Interactive chat with the AI assistant
- **Session Management**: Automatic session creation and tracking
- **Customer Information**: Optional customer info collection at session start
- **Health Monitoring**: Real-time API connection status
- **Escalation Support**: Direct escalation to human agents when needed
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional interface with smooth animations

## Usage

1. **Start the API Server**:
   ```bash
   cd /Users/tcetokalak/Projects/github/supportflow
   python -m uvicorn src.supportflow.api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open the Interface**:
   - Open `index.html` in your web browser
   - Or serve it with a simple HTTP server:
     ```bash
     cd agentpanel
     python -m http.server 8080
     ```
   - Navigate to `http://localhost:8080`

## Configuration

The interface connects to the API at `http://localhost:8000` by default. To change this, modify the `apiBaseUrl` in `script.js`:

```javascript
this.apiBaseUrl = 'http://your-api-server:port';
```

## Features Overview

### Chat Interface
- Send messages to the AI assistant
- View conversation history
- Quick action buttons for common queries
- Real-time typing indicators and loading states

### Session Management
- Automatic session creation on first message
- Session status monitoring
- Session information display
- Start new sessions with customer information

### Customer Information
- Optional customer details collection
- Name, phone, email, and account number fields
- Skip option for anonymous sessions

### Escalation
- Automatic escalation detection
- Manual escalation to human agents
- Escalation reason tracking

### Health Monitoring
- Real-time API connection status
- Ollama service status
- Connection retry logic

## File Structure

```
agentpanel/
├── index.html          # Main HTML interface
├── styles.css          # CSS styling and animations
├── script.js           # JavaScript functionality
└── README.md          # This documentation
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## API Integration

The interface integrates with the following API endpoints:

- `POST /chat` - Send chat messages
- `GET /session/{session_id}/status` - Get session status
- `POST /session/{session_id}/escalate` - Escalate to human
- `GET /health` - Check API health

## Customization

### Styling
Modify `styles.css` to customize the appearance. The CSS uses CSS custom properties (variables) for easy theming.

### Functionality
Extend `script.js` to add new features or modify existing behavior.

### Quick Actions
Add or modify quick action buttons in `index.html` by adding buttons with `data-message` attributes.

## Troubleshooting

### Connection Issues
- Ensure the API server is running on `http://localhost:8000`
- Check browser console for error messages
- Verify CORS settings in the API configuration

### Session Problems
- Sessions expire after inactivity
- Clear browser storage to reset session state
- Check session status using the status button

### Chat Issues
- Ensure Ollama is running and accessible
- Check API logs for error messages
- Verify model availability (gemma3:latest)
