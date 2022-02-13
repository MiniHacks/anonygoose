
import { useForm, UseFormRegisterReturn } from 'react-hook-form'
import { InputGroup } from '@chakra-ui/react';

export default function FileUpload(register) {
  const inputRef = useRef(null)
  const { ref, ...rest } = register

  const handleClick = () => inputRef.current.click();

  return (
    <InputGroup onClick={handleClick}>
        <input
            type={'file'}
            multiple={true}
            hidden
            {...rest}
            ref={(e) => {
                ref(e)
                inputRef.current = e
            }}
        />
    </InputGroup>
  )

}