
require("entry-points/plugin-common");

import React from "react";

import init_plugin from "init-plugin";
import MainContainer from "./component";
import App from "./store";
import rootSaga from "./root-saga";


init_plugin(
    App,
    rootSaga,
    document.getElementById('root'),
    <MainContainer />,
    () => {}
);
