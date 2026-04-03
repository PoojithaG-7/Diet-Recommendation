# User Data Dashboard

A standalone dashboard for viewing all registered users' data in the Diet Recommendation System.

## 🚀 Quick Start

### Method 1: Open Directly (Recommended)
1. Double-click on `dashboard.html` - it will open in your browser
2. Or run `open_dashboard.bat` to open it automatically

### Method 2: Using Python Server
```bash
cd "c:\project4\Diet Recommendation System\user_dashboard"
python simple_dashboard.py
```
Then visit `http://localhost:5001`

## 📋 Prerequisites

- Main Diet Recommendation System must be running on `http://localhost:5000`
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for Bootstrap CDN)

## ✨ Features

### 📊 Real-time Statistics
- **Total Users**: Number of registered users
- **Active Users**: Users who completed their diet plan
- **Inactive Users**: Users who haven't completed their diet plan
- **Average Age**: Average age of all users

### 👥 User Information Table
- **Name**: User's full name
- **Email**: User's email address
- **Age**: User's age
- **Gender**: User's gender
- **Weight**: User's weight in kg
- **Height**: User's height in cm
- **BMI**: User's Body Mass Index
- **Goal**: User's fitness goal
- **Activity Level**: User's activity level
- **Phone**: User's phone number
- **Daily Calories**: User's daily calorie needs
- **Status**: Active/Inactive status

### 🔄 Auto-Refresh
- Data automatically refreshes every 30 seconds
- Manual refresh button available
- Last updated timestamp shown

### 🎨 Modern UI
- Beautiful gradient design
- Responsive layout
- Hover effects and animations
- Status indicators
- Emoji icons for better visualization

## 🔧 Configuration

The dashboard connects to the main system using these settings (in dashboard.html):

```javascript
const MAIN_SYSTEM_URL = "http://localhost:5000";
const ADMIN_EMAIL = "admin@diet-system.com";
const ADMIN_PASSWORD = "admin123";
```

## 📱 Access Methods

### 1. Direct HTML File (Easiest)
- Open `dashboard.html` directly in your browser
- No server required
- Works immediately

### 2. Python Server
- Run `simple_dashboard.py`
- Visit `http://localhost:5001`
- More robust for production

### 3. Batch File (Windows)
- Double-click `open_dashboard.bat`
- Automatically opens dashboard.html

## 🔍 Data Sources

The dashboard fetches data from the main Diet Recommendation System:

1. **Authentication**: Uses admin credentials to get access token
2. **User Profile**: Fetches user profile data from `/api/auth/profile`
3. **Processing**: Extracts and formats user information
4. **Display**: Shows data in beautiful, readable format

## 🛡️ Security

- Uses admin credentials from the main system
- Token-based authentication
- Read-only access (no modifications possible)
- Secure communication with main system
- No data stored in dashboard

## 🚨 Troubleshooting

### Connection Issues
If you see connection errors:

1. **Check Main System**: Ensure Diet Recommendation System is running on `http://localhost:5000`
2. **Verify Admin Access**: Confirm admin credentials are correct
3. **Check Network**: Ensure no firewall blocking localhost connections
4. **Browser Console**: Check for JavaScript errors (F12 → Console)

### Data Not Loading
If data doesn't load:

1. **Refresh Page**: Click the refresh button or reload the page
2. **Check Console**: Look for error messages in browser console
3. **Verify Main System**: Ensure main system is working properly
4. **Check Credentials**: Verify admin email and password are correct

### Display Issues
If the dashboard looks broken:

1. **Browser Compatibility**: Use a modern browser (Chrome, Firefox, Safari, Edge)
2. **JavaScript Enabled**: Ensure JavaScript is enabled in browser
3. **Clear Cache**: Clear browser cache and reload
4. **Check Internet**: Ensure internet connection for Bootstrap CDN

## 📊 Understanding the Data

### User Status
- **Active**: User has completed their diet plan (has weight and height)
- **Inactive**: User hasn't completed their diet plan

### BMI Categories
- **Underweight**: BMI < 18.5
- **Normal**: BMI 18.5-24.9
- **Overweight**: BMI 25-29.9
- **Obese**: BMI ≥ 30

### Activity Levels
- **Sedentary**: Little or no exercise
- **Light**: Light exercise/sports 1-3 days/week
- **Moderate**: Moderate exercise/sports 3-5 days/week
- **Active**: Hard exercise/sports 6-7 days a week

### Goals
- **Weight Loss**: Reduce body weight
- **Maintenance**: Maintain current weight
- **Muscle Gain**: Increase muscle mass
- **Health**: Improve overall health

## 🔄 Advanced Features

### Auto-Refresh
- Automatically refreshes data every 30 seconds
- Ensures you always see the latest user information
- Can be disabled by commenting out the setInterval line

### Export Data
You can export data by:
1. Copy-pasting from the table
2. Using browser print function to save as PDF
3. Taking screenshots for reports

### Multiple Users
The dashboard can display multiple users if the main system has:
- Multiple registered users
- Proper user management system
- Admin access to all user data

## 🎯 Use Cases

### System Administration
- Monitor user registration and activity
- Track diet plan completion rates
- Analyze user demographics
- Identify inactive users

### Health Monitoring
- Track user health metrics
- Monitor BMI trends
- Analyze goal distribution
- Review activity levels

### Business Analytics
- User growth tracking
- Engagement metrics
- Demographic analysis
- Performance monitoring

## 📝 Development Notes

### File Structure
```
user_dashboard/
├── dashboard.html          # Main dashboard (HTML + JavaScript)
├── simple_dashboard.py     # Python server version
├── app.py                  # Advanced Flask server
├── open_dashboard.bat      # Windows batch file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

### Customization
To customize the dashboard:

1. **Edit dashboard.html** for UI changes
2. **Modify JavaScript** for data processing
3. **Update CSS** for styling changes
4. **Add new features** as needed

### Extensions
You can extend the dashboard with:
- User search and filtering
- Data export functionality
- Historical data tracking
- Advanced analytics
- User management features

## 🆘 Support

For issues or questions:

1. **Check this README** for common solutions
2. **Verify main system** is running properly
3. **Test admin credentials** in main system
4. **Check browser console** for errors
5. **Try different browser** if issues persist

## 📄 License

This dashboard is part of the Diet Recommendation System project.

---

**🎉 Enjoy monitoring your users with this beautiful dashboard!**
