import ReactSwitch from "react-switch";
import ReactCountryFlag from "react-country-flag";

const FlagSwitch = (props) => {
    const handleChange = (checked) => {
        props.setChecked(checked);

        props.setValues((values) => ({
            ...values,
            'lang': checked ? "pt" : "en",
        }));
    };

    return (
        <ReactSwitch
            checked={props.checked}
            onChange={handleChange}
            className="react-switch"
            handleDiameter={70}
            offColor="#ededed"
            onColor="#ededed"
            offHandleColor="#a8a8a8"
            onHandleColor="#a8a8a8"
            height={70}
            width={170}
            borderRadius={8}
            checkedIcon={<div className="icons-switch">PT</div>}
            uncheckedIcon={<div className="icons-switch">EN</div>}
            checkedHandleIcon={
                <div className="icons-switch">
                    <ReactCountryFlag countryCode="PT" svg/>
                </div>
            }
            uncheckedHandleIcon={
                <div className="icons-switch">
                    <ReactCountryFlag style={{fontSize: "20px"}} countryCode="GB" svg/>
                    <ReactCountryFlag
                        style={{paddingLeft: "10px", fontSize: "20px"}}
                        countryCode="US"
                        svg
                    />
                </div>
            }
        />
    );
};

export default FlagSwitch;
