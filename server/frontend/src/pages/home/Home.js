import {Container, Row, Col} from "react-bootstrap";
import Layout from "../../templates/Layouts/Layout";
import Sidebar from "../../templates/Sidebar/Sidebar";
import Title from "../../templates/Sidebar/Title";
import TextHomepage from "../../templates/Textual/TextHomepage";

const Home = (props) => {
    return (
        <Layout
            main={
                <Container fluid={true} className="pb-5">
                    <Title title={"Journalistic Narratives Extraction"}/>
                    <Row className="mt-5 mx-2 mx-lg-0 min-vh-70">
                        <Sidebar/>
                        <Col lg={9}
                             className="text-justify enhanced-body-background-color rounded-corners px-4 px-lg-5 pt-5 pb-3">
                            <TextHomepage/>
                        </Col>
                    </Row>
                </Container>
            }
        />
    );
};

export default Home;
