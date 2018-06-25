
require("entry-points/plugin-common");

import init_plugin from "init-plugin";
import MainContainer from "./component";


init_plugin(
  document.getElementById('root'),
  <MainContainer />
);
