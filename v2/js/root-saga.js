
import { takeLatest, takeEvery } from 'redux-saga';
import { put, select } from "redux-saga/effects";

import * as actions from "actions/ActionWrapper";
import { requestConfig } from "sagas/ActionWrapper";


function* rootSaga() {
  yield [
    takeLatest(actions.GET_ACTIONS_CONFIG, requestConfig),
  ];
}

export default rootSaga;

