# Diet Recommendation System

A React-based web application for personalized diet recommendations and nutrition tracking.

## Features

- **Home Page**: Landing page with feature overview and call-to-action
- **User Authentication**: Login and registration forms with validation
- **Diet Form**: Comprehensive form to collect health information and generate personalized diet plans
- **Dashboard**: Interactive dashboard to track progress, view nutrition goals, and monitor daily intake
- **Responsive Design**: Mobile-friendly interface using Bootstrap

## Technology Stack

- **Frontend**: React 18.2.0
- **Styling**: Bootstrap 5.3.0 with React Bootstrap 2.7.0
- **Routing**: React Router DOM 6.8.0
- **Build Tool**: Create React App

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd diet-recommendation-system
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open your browser and navigate to `http://localhost:3000`

## Project Structure

```
diet-recommendation-system/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── Navigation.js
│   ├── pages/
│   │   ├── Home.js
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── DietForm.js
│   │   └── Dashboard.js
│   ├── App.css
│   ├── App.js
│   └── index.js
├── package.json
└── README.md
```

## Pages Overview

### Home Page
- Hero section with welcome message
- Feature cards highlighting key benefits
- How-it-work section
- Call-to-action buttons

### Login Page
- Email and password fields
- Remember me checkbox
- Link to registration page
- Form validation and error handling

### Register Page
- Comprehensive registration form
- Personal information fields
- Password confirmation
- Form validation

### Diet Form Page
- Health information collection (weight, height, age, gender)
- Activity level and goal selection
- Dietary restrictions and allergies
- Medical conditions
- Personalized recommendation generation with:
  - BMI calculation
  - Daily calorie needs
  - Macronutrient breakdown
  - Sample meal plans
  - Health tips

### Dashboard Page
- User statistics overview
- Daily nutrition progress bars
- Weight loss progress tracking
- Recent meals log
- Weekly progress table
- Quick action buttons
- Health tips section

## Features Implemented

### Navigation
- Responsive navbar with brand logo
- Navigation links to all main pages
- Account dropdown menu
- Fixed positioning for easy access

### Form Validation
- Client-side validation for all forms
- Error handling and user feedback
- Loading states during form submission

### Responsive Design
- Mobile-first approach
- Bootstrap grid system
- Responsive cards and components
- Optimized for all screen sizes

### Interactive Elements
- Hover effects on cards
- Progress bars for tracking
- Dynamic content updates
- Smooth transitions

## Future Enhancements

- Backend API integration
- User authentication with JWT
- Database integration for data persistence
- Advanced analytics and reporting
- Recipe recommendations
- Social features and community
- Mobile app development

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue in the repository.
