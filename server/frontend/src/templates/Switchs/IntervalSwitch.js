import { Col, Row, ToggleButton } from 'react-bootstrap'
const IntervalSwitch = (props) => {

    const options = [
        { name: 'Incremental', value: "1" },
        { name: 'By interval', value: "2" }
      ];

    return (
        <Row className="mb-3">
            {options.map((option, index) => (
                <Col key={index}>
                    <ToggleButton
                        key={index}
                        id={`mode-${index}`}
                        type="radio"
                        name="mode"
                        value={option.value}
                        checked={props.mode === option.value}
                        onChange={(e) => props.handleSelect(e.currentTarget.value)}
                        style={{display: "block"}}
                        variant={props.mode === option.value ? 'light-blue' : 'outline-secondary'}
                    >
                        {option.name}
                    </ToggleButton>
                </Col>
            ))}
        </Row>
    );
};

export default IntervalSwitch;
