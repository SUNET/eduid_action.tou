
import { combineReducers } from 'redux';
import { intlReducer } from 'react-intl-redux'
import { reducer as formReducer } from 'redux-form';
import { routerReducer } from 'react-router-redux';

import notificationsReducer from 'reducers/Notifications';

const App = combineReducers({
    router: routerReducer,
    form: formReducer,
    intl: intlReducer,
    notifications: notificationsReducer
});

export default App;

