import { Button, Spinner, Table } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Link } from "react-router-dom"

const TableTopics = (props) => {

    const formatDatetime = (datetime) => {
        // Convert from ISO to local and then to YYYY-MM-DD hh:mm
        datetime = new Date(datetime);
        let dd = datetime.getDate(); // day of the month
        let MM = datetime.getMonth() + 1; // getMonth() is zero-based
        let hh = datetime.getHours();
        let mm = datetime.getMinutes();

        return  [datetime.getFullYear(), '-',
        (MM>9 ? '' : '0') + MM, '-' ,
        (dd>9 ? '' : '0') + dd,
        ' ',
        (hh>9 ? '' : '0') + hh, ':',
        (mm>9 ? '' : '0') + mm
        ].join('');
    }

    const languageFlags = {
        "pt": '🇵🇹',
        "en": '🇬🇧'
    }

    return (
        <Table striped bordered hover>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Topic</th>
                    <th>Language</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    {props.editable && <th>Status</th>}
                    <th>Options</th>
                    {props.editable && <th></th>}
                </tr>
            </thead>
            <tbody>
                {props.topics.map((topic, index) => (
                    <>
                    {/*{(topic.tag === "Queen Elizabeth death" || topic.tag === "seleção portugal espanha") &&
                    */}
                <>
                <tr key={index}>
                    <td>{index}</td>
                    <td>{topic.tag}</td>
                    <td>{languageFlags[topic.lang]} {topic.lang.toUpperCase()}</td>
                    <td>{topic.start_date !== 0 ? formatDatetime(topic.start_date) : ""}</td>
                    <td>{topic.end_date !== 0 ? formatDatetime(topic.end_date) : ""}</td>
                    
                    {props.editable && <td>
                        {(!topic.active && !topic.finished) &&
                            <Button variant="success" onClick={() => {props.startCallback(topic.es_id)}}>
                                <FontAwesomeIcon icon="fas fa-play"/> Start
                            </Button>
                        }
                        {topic.active &&
                            <Button variant="primary" disabled={topic.finished}>
                                <Spinner as="span" size="sm" animation="border"/> In progress...
                            </Button>
                        }
                        {topic.finished && 
                            <Button variant="success">
                                <FontAwesomeIcon icon="fas fa-check"/> Completed
                            </Button>
                        }
                    </td>}
                    
                    <td>
                        <Link to={"/topic/"+topic.es_id}>
                            <Button>
                                <FontAwesomeIcon icon="fas fa-up-right-from-square" /> Open
                            </Button>
                        </Link>
                    </td>

                    {props.editable && <td>
                        {topic.active 
                        ?
                            <Button variant="danger" disabled={topic.finished} onClick={() => {props.stopCallback(topic.es_id)}}>
                                <FontAwesomeIcon icon="fas fa-stop" /> Stop
                            </Button>
                        :
                            <Button variant="danger" onClick={() => {props.deleteCallback(topic.es_id)}}>
                                    <FontAwesomeIcon icon="fas fa-trash-can" />
                            </Button>
                        }
                    </td>}
                </tr>
                </>
                </>
                ))}
            </tbody>
        </Table>
    )
};

export default TableTopics;