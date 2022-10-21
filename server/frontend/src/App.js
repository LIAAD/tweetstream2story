import { HashRouter as Router, Switch, Route } from "react-router-dom";
import About from "./pages/about/About";
import Examples from "./pages/examples/Examples"
import Tweet2Story from "./pages/tweet2story/Tweet2Story";
import Topic from "./pages/topic/Topic";
import { library } from '@fortawesome/fontawesome-svg-core'
import { faAngleDown, faCheck, faPencil, faPlay, faStop, faTrashCan, faUpRightFromSquare, faExpandAlt } from '@fortawesome/free-solid-svg-icons'
import { v4 as uuidv4 } from 'uuid';
const App = () => {

  // Store session id used for requests
  if(localStorage.getItem("session") === null) {
    localStorage.setItem("session", uuidv4());
  }
  
  // FontAwesome Icons
  library.add( faAngleDown, faCheck, faPencil, faPlay, faStop, faTrashCan, faUpRightFromSquare, faExpandAlt )

  return (
    <Router>
      <Switch>
        <Route exact path="/">
          <Tweet2Story/>
        </Route>
        <Route path="/about">
          <About/>
        </Route>
        <Route path="/examples">
          <Examples/>
        </Route>
        <Route path="/topic/:id" children={<Topic />}/>
      </Switch>
    </Router>
  );
};

export function handleChange(e, setValues) {
  e.preventDefault();

  const key = e.target.name;
  const value = e.target.value;
  setValues((values) => ({
    ...values,
    [key]: value,
  }));
}

export default App;
