
import { combineReducers } from 'redux';
import { intlReducer } from 'react-intl-redux'
import { routerReducer } from 'react-router-redux';

import actionWrapperReducer from 'reducers/ActionWrapper';
import notificationsReducer from 'reducers/Notifications';

const App = combineReducers({
    router: routerReducer,
    intl: intlReducer,
    main: actionWrapperReducer,
    notifications: notificationsReducer
});

export default App;

