
import { InputGroup } from '@chakra-ui/react';
import { useRef } from 'react';

export default function FileUpload(register, accept, children) {
  const inputRef = useRef(null)
  const { ref, ...rest } = register

  const handleClick = () => inputRef.current.click();

  return (
    <InputGroup onClick={handleClick}>
        <input
            type={'file'}
            multiple={true}
            hidden
            accept={accept}
            {...rest}
            ref={(e) => {
                ref(e)
                inputRef.current = e
            }}
        />
        <> {children} </>
    </InputGroup>
  )

}