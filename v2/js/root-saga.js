
import { takeLatest, takeEvery } from 'redux-saga';
import { put, select } from "redux-saga/effects";

import * as actions from "actions/ActionWrapper";
import { requestConfig } from "sagas/ActionWrapper";
import * as component from "./component";


function* postAcceptTOU () {
}


function* rootSaga() {
  yield [
    takeLatest(actions.GET_ACTIONS_CONFIG, requestConfig),
    takeLatest(component.TOU_ACCEPTED, postAcceptTOU),
  ];
}

export default rootSaga;

